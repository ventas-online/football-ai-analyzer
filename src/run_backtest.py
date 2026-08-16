import json
from pathlib import Path
import pandas as pd

from .pipeline import walk_forward_predictions
from .backtest import evaluate_1x2
from .market_backtest import evaluate_markets, calibration_bins, rank_signal_filters


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
        "model_version": "ensemble-v2",
        "matches_input": len(matches),
        "predictions_evaluated": len(rows),
        "metrics_1x2": report,
        "metrics_markets": markets,
        "calibration": calibration,
        "signal_ranking": signal_ranking,
        "signal_policy": {
            "min_samples": 30,
            "keep_for_review": "hit_rate >= 0.60 and calibration_gap >= -0.05",
            "drop": "hit_rate < 0.55 or calibration_gap < -0.10",
            "warning": "These are out-of-sample research filters, not profitability or guaranteed-win claims."
        },
        "note": "ROI/edge is intentionally not reported because this data source does not provide bookmaker odds.",
    }
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    Path("data/reports/backtest.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
