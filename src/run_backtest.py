import json
from pathlib import Path
import pandas as pd

from .pipeline import walk_forward_predictions
from .backtest import evaluate_1x2
from .market_backtest import evaluate_markets, calibration_bins, rank_signal_filters


def _baseline_1x2(frame):
    """Majority-class baseline calculated only on the evaluation sample."""
    if frame.empty:
        return {"samples": 0}
    majority = frame["actual"].mode().iloc[0]
    return {
        "samples": len(frame),
        "majority_class": majority,
        "accuracy": float((frame["actual"] == majority).mean()),
    }


def _season_metrics(frame):
    """Break results down by season without changing the walk-forward order."""
    if frame.empty or "utc_date" not in frame:
        return {}
    dates = pd.to_datetime(frame["utc_date"], utc=True, errors="coerce")
    # Football-data.org season labels are not always present in the normalized rows;
    # derive a compact calendar-year diagnostic rather than inventing season labels.
    tmp = frame.copy()
    tmp["calendar_year"] = dates.dt.year
    result = {}
    for year, group in tmp.groupby("calendar_year", dropna=True):
        result[str(int(year))] = evaluate_1x2(group)
    return result


def _confidence_bands(frame):
    """Evaluate whether high model confidence actually corresponds to outcomes."""
    if frame.empty:
        return {}
    bands = [(0.50, 0.60), (0.60, 0.70), (0.70, 0.80), (0.80, 1.01)]
    rows = []
    for lo, hi in bands:
        candidates = []
        for _, r in frame.iterrows():
            probs = {"H": r["p_home"], "D": r["p_draw"], "A": r["p_away"]}
            label, prob = max(probs.items(), key=lambda x: x[1])
            if lo <= float(prob) < hi:
                candidates.append((label, float(prob), r["actual"]))
        if candidates:
            rows.append({
                "range": f"{lo:.2f}-{min(hi, 1.0):.2f}",
                "samples": len(candidates),
                "mean_probability": sum(x[1] for x in candidates) / len(candidates),
                "hit_rate": sum(x[0] == x[2] for x in candidates) / len(candidates),
            })
    return rows


def _market_confidence_diagnostics(rows):
    """Report calibration gaps at progressively stricter thresholds."""
    definitions = {
        "over_25": ("p_over_25", lambda r: r["home_goals"] + r["away_goals"] >= 3),
        "btts_yes": ("p_btts_yes", lambda r: r["home_goals"] >= 1 and r["away_goals"] >= 1),
    }
    out = {}
    for market, (key, outcome) in definitions.items():
        bands = []
        for lo, hi in ((0.50, 0.60), (0.60, 0.70), (0.70, 0.80), (0.80, 1.01)):
            selected = [r for r in rows if lo <= float(r[key]) < hi]
            if not selected:
                continue
            p = sum(float(r[key]) for r in selected) / len(selected)
            hit = sum(bool(outcome(r)) for r in selected) / len(selected)
            bands.append({
                "range": f"{lo:.2f}-{min(hi, 1.0):.2f}",
                "samples": len(selected),
                "mean_probability": round(p, 6),
                "observed_rate": round(hit, 6),
                "calibration_gap": round(hit - p, 6),
            })
        out[market] = bands
    return out


def main():
    path = Path("data/raw/matches.json")
    if not path.exists():
        raise SystemExit("No existe data/raw/matches.json")

    matches = json.loads(path.read_text(encoding="utf-8"))
    rows = walk_forward_predictions(matches)
    frame = pd.DataFrame(rows)
    report = evaluate_1x2(frame) if rows else {"samples": 0}

    markets = evaluate_markets(rows)
    calibration = {
        "over_25": calibration_bins(rows, "p_over_25", lambda r: r["home_goals"] + r["away_goals"] >= 3),
        "btts_yes": calibration_bins(rows, "p_btts_yes", lambda r: r["home_goals"] >= 1 and r["away_goals"] >= 1),
    }
    signal_ranking = rank_signal_filters(rows, min_samples=30)

    output = {
        "model_version": "ensemble-v3-form-elo-poisson-mc",
        "evaluation_design": {
            "method": "strict_walk_forward",
            "future_leakage": False,
            "historical_seasons_requested": [2021, 2022, 2023, 2024, 2025],
            "minimum_signal_sample": 30,
        },
        "matches_input": len(matches),
        "predictions_evaluated": len(rows),
        "metrics_1x2": report,
        "baseline_1x2": _baseline_1x2(frame),
        "calendar_period_metrics": _season_metrics(frame),
        "confidence_diagnostics_1x2": _confidence_bands(frame),
        "metrics_markets": markets,
        "calibration": calibration,
        "market_confidence_diagnostics": _market_confidence_diagnostics(rows),
        "signal_ranking": signal_ranking,
        "signal_policy": {
            "min_samples": 30,
            "keep_for_review": "hit_rate >= 0.60 and calibration_gap >= -0.05",
            "drop": "hit_rate < 0.55 or calibration_gap < -0.10",
            "warning": "Research filters only; no guarantee of winning or profitability.",
        },
        "next_required_input_for_roi": "historical bookmaker odds or a permitted odds feed",
        "note": "ROI and edge are intentionally absent until real market odds are available.",
    }
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    Path("data/reports/backtest.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
