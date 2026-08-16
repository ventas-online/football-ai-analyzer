from .pipeline import walk_forward_predictions
from .report import summarize_predictions


def build_dashboard_payload(matches):
    rows = walk_forward_predictions(matches)
    summary = summarize_predictions(rows)
    upcoming = []
    return {
        "summary": summary,
        "historical_predictions": rows[-50:],
        "upcoming": upcoming,
        "model_version": "ensemble-v1",
    }
