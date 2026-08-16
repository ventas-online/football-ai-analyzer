import json
from pathlib import Path

from .pipeline import walk_forward_predictions
from .backtest import evaluate_1x2


def main():
    path = Path("data/raw/matches.json")
    if not path.exists():
        raise SystemExit("No existe data/raw/matches.json")

    matches = json.loads(path.read_text(encoding="utf-8"))
    rows = walk_forward_predictions(matches)
    report = evaluate_1x2(__import__("pandas").DataFrame(rows)) if rows else {"samples": 0}

    output = {
        "model_version": "ensemble-v1",
        "matches_input": len(matches),
        "predictions_evaluated": len(rows),
        "metrics_1x2": report,
    }
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    Path("data/reports/backtest.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
