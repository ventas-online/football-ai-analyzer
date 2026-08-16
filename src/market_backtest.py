import math


def _brier_binary(rows, probability_key, outcome_fn):
    if not rows:
        return None
    errors = []
    for row in rows:
        p = float(row[probability_key])
        y = 1.0 if outcome_fn(row) else 0.0
        errors.append((p - y) ** 2)
    return sum(errors) / len(errors)


def _accuracy_threshold(rows, probability_key, outcome_fn, threshold):
    selected = [r for r in rows if float(r[probability_key]) >= threshold]
    if not selected:
        return {"samples": 0, "hit_rate": None}
    hits = sum(bool(outcome_fn(r)) for r in selected)
    return {"samples": len(selected), "hit_rate": hits / len(selected)}


def evaluate_markets(rows):
    if not rows:
        return {"samples": 0}

    over = lambda r: r["home_goals"] + r["away_goals"] >= 3
    btts = lambda r: r["home_goals"] >= 1 and r["away_goals"] >= 1
    return {
        "samples": len(rows),
        "over_25": {
            "brier": _brier_binary(rows, "p_over_25", over),
            "thresholds": {str(t): _accuracy_threshold(rows, "p_over_25", over, t) for t in (0.60, 0.65, 0.70, 0.75)},
        },
        "btts_yes": {
            "brier": _brier_binary(rows, "p_btts_yes", btts),
            "thresholds": {str(t): _accuracy_threshold(rows, "p_btts_yes", btts, t) for t in (0.60, 0.65, 0.70, 0.75)},
        },
    }


def calibration_bins(rows, probability_key, outcome_fn, bins=10):
    """Return reliability data for probability calibration."""
    result = []
    for i in range(bins):
        lo, hi = i / bins, (i + 1) / bins
        bucket = [r for r in rows if lo <= float(r[probability_key]) < hi or (i == bins - 1 and float(r[probability_key]) == 1)]
        if not bucket:
            continue
        result.append({
            "range": f"{lo:.1f}-{hi:.1f}",
            "samples": len(bucket),
            "mean_probability": sum(float(r[probability_key]) for r in bucket) / len(bucket),
            "observed_rate": sum(bool(outcome_fn(r)) for r in bucket) / len(bucket),
        })
    return result
