import json
from pathlib import Path
import pandas as pd

from .pipeline import walk_forward_predictions
from .backtest import evaluate_1x2
from .market_backtest import evaluate_markets, calibration_bins, rank_signal_filters
from .odds_loader import load_odds
from .value_engine import evaluate as evaluate_value
from .report_engine import summarize_signals


def _baseline_1x2(frame):
    if frame.empty:
        return {"samples": 0}
    majority = frame["actual"].mode().iloc[0]
    return {"samples": len(frame), "majority_class": majority, "accuracy": float((frame["actual"] == majority).mean())}


def _season_metrics(frame):
    if frame.empty or "utc_date" not in frame:
        return {}
    dates = pd.to_datetime(frame["utc_date"], utc=True, errors="coerce")
    tmp = frame.copy(); tmp["calendar_year"] = dates.dt.year
    return {str(int(y)): evaluate_1x2(g) for y, g in tmp.groupby("calendar_year", dropna=True)}


def _confidence_bands(frame):
    if frame.empty:
        return []
    rows = []
    for lo, hi in ((.50,.60),(.60,.70),(.70,.80),(.80,1.01)):
        candidates=[]
        for _, r in frame.iterrows():
            probs={"H":r["p_home"],"D":r["p_draw"],"A":r["p_away"]}; label,prob=max(probs.items(), key=lambda x:x[1])
            if lo <= float(prob) < hi: candidates.append((label,float(prob),r["actual"]))
        if candidates:
            rows.append({"range":f"{lo:.2f}-{min(hi,1):.2f}","samples":len(candidates),"mean_probability":sum(x[1] for x in candidates)/len(candidates),"hit_rate":sum(x[0]==x[2] for x in candidates)/len(candidates)})
    return rows


def _market_confidence_diagnostics(rows):
    definitions={"over_25":("p_over_25",lambda r:r["home_goals"]+r["away_goals"]>=3),"btts_yes":("p_btts_yes",lambda r:r["home_goals"]>=1 and r["away_goals"]>=1)}
    out={}
    for market,(key,outcome) in definitions.items():
        bands=[]
        for lo,hi in ((.50,.60),(.60,.70),(.70,.80),(.80,1.01)):
            selected=[r for r in rows if lo<=float(r[key])<hi]
            if selected:
                p=sum(float(r[key]) for r in selected)/len(selected); hit=sum(bool(outcome(r)) for r in selected)/len(selected)
                bands.append({"range":f"{lo:.2f}-{min(hi,1):.2f}","samples":len(selected),"mean_probability":round(p,6),"observed_rate":round(hit,6),"calibration_gap":round(hit-p,6)})
        out[market]=bands
    return out


def _attach_value(rows, odds):
    """Join pre-match market odds by match identity and calculate fair odds/EV.
    Odds are never invented; absent odds remain ODDS_REQUIRED.
    """
    odds = odds or {}
    enriched=[]
    for r in rows:
        date=str(r.get("utc_date", r.get("date", "")))[:10]
        home=str(r.get("home_team", "")).strip(); away=str(r.get("away_team", "")).strip()
        for market,key in (("over_25","p_over_25"),("btts_yes","p_btts_yes")):
            market_odds=odds.get((date,home,away,market))
            sig=evaluate_value(market,float(r[key]),market_odds)
            outcome=(r["home_goals"]+r["away_goals"]>=3) if market=="over_25" else (r["home_goals"]>=1 and r["away_goals"]>=1)
            enriched.append({"date":date,"home_team":home,"away_team":away,"market":market,"probability":float(r[key]),"fair_odds":sig.fair_odds,"market_odds":market_odds,"edge":sig.edge,"ev":sig.ev,"status":sig.status,"won":bool(outcome)})
    return enriched


def main():
    path=Path("data/raw/matches.json")
    if not path.exists(): raise SystemExit("No existe data/raw/matches.json")
    matches=json.loads(path.read_text(encoding="utf-8")); rows=walk_forward_predictions(matches); frame=pd.DataFrame(rows)
    report=evaluate_1x2(frame) if rows else {"samples":0}
    markets=evaluate_markets(rows)
    calibration={"over_25":calibration_bins(rows,"p_over_25",lambda r:r["home_goals"]+r["away_goals"]>=3),"btts_yes":calibration_bins(rows,"p_btts_yes",lambda r:r["home_goals"]>=1 and r["away_goals"]>=1)}
    signal_ranking=rank_signal_filters(rows,min_samples=30)
    odds_path=Path("data/odds/historical_odds.csv")
    odds=load_odds(str(odds_path)) if odds_path.exists() else {}
    value_rows=_attach_value(rows,odds)
    value_report=summarize_signals(value_rows)
    output={"model_version":"ensemble-v3-form-elo-poisson-mc","evaluation_design":{"method":"strict_walk_forward","future_leakage":False,"historical_seasons_requested":[2021,2022,2023,2024,2025],"minimum_signal_sample":30},"matches_input":len(matches),"predictions_evaluated":len(rows),"metrics_1x2":report,"baseline_1x2":_baseline_1x2(frame),"calendar_period_metrics":_season_metrics(frame),"confidence_diagnostics_1x2":_confidence_bands(frame),"metrics_markets":markets,"calibration":calibration,"market_confidence_diagnostics":_market_confidence_diagnostics(rows),"signal_ranking":signal_ranking,"value_analysis":{"odds_file_present":odds_path.exists(),"odds_rows_loaded":len(odds),"signals":value_report},"signal_policy":{"min_samples":30,"keep_for_review":"hit_rate >= 0.60 and calibration_gap >= -0.05","drop":"hit_rate < 0.55 or calibration_gap < -0.10"},"note":"ROI/EV are reported only where real historical odds exist; missing odds produce ODDS_REQUIRED."}
    Path("data/reports").mkdir(parents=True,exist_ok=True); Path("data/reports/backtest.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps(output,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
