import math


THRESHOLDS = (0.60, 0.65, 0.70, 0.75)


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
            "thresholds": {str(t): _accuracy_threshold(rows, "p_over_25", over, t) for t in THRESHOLDS},
        },
        "btts_yes": {
            "brier": _brier_binary(rows, "p_btts_yes", btts),
            "thresholds": {str(t): _accuracy_threshold(rows, "p_btts_yes", btts, t) for t in THRESHOLDS},
        },
    }


def _rank_threshold(rows, probability_key, outcome_fn, threshold, min_samples=30):
    """Evaluate one high-probability signal filter without bookmaker odds.

    This is a research filter, not a profitability claim. A signal is only
    eligible for review after enough out-of-sample observations exist.
    """
    selected = [r for r in rows if float(r[probability_key]) >= threshold]
    n = len(selected)
    if not n:
        return {
            "threshold": threshold,
            "samples": 0,
            "mean_probability": None,
            "hit_rate": None,
            "calibration_gap": None,
            "brier": None,
            "status": "NO_DATA",
        }

    probabilities = [float(r[probability_key]) for r in selected]
    outcomes = [1.0 if outcome_fn(r) else 0.0 for r in selected]
    mean_probability = sum(probabilities) / n
    hit_rate = sum(outcomes) / n
    calibration_gap = hit_rate - mean_probability
    brier = sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / n

    if n < min_samples:
        status = "INSUFFICIENT_SAMPLE"
    elif hit_rate >= 0.60 and calibration_gap >= -0.05:
        status = "KEEP_FOR_REVIEW"
    elif hit_rate < 0.55 or calibration_gap < -0.10:
        status = "DROP"
    else:
        status = "REVIEW"

    return {
        "threshold": threshold,
        "samples": n,
        "mean_probability": round(mean_probability, 6),
        "hit_rate": round(hit_rate, 6),
        "calibration_gap": round(calibration_gap, 6),
        "brier": round(brier, 6),
        "status": status,
    }


def rank_signal_filters(rows, min_samples=30):
    """Rank candidate high-confidence filters from strictly out-of-sample rows.

    No bookmaker odds are used, so KEEP_FOR_REVIEW means statistically
    promising for further validation, not profitable or guaranteed.
    """
    if not rows:
        return {"min_samples": min_samples, "markets": {}}

    definitions = {
        "over_25": ("p_over_25", lambda r: r["home_goals"] + r["away_goals"] >= 3),
        "btts_yes": ("p_btts_yes", lambda r: r["home_goals"] >= 1 and r["away_goals"] >= 1),
    }
    markets = {}
    for market, (probability_key, outcome_fn) in definitions.items():
        ranked = [
            _rank_threshold(rows, probability_key, outcome_fn, threshold, min_samples)
            for threshold in THRESHOLDS
        ]
        markets[market] = sorted(
            ranked,
            key=lambda x: (
                x["status"] == "KEEP_FOR_REVIEW",
                x["hit_rate"] if x["hit_rate"] is not None else -1,
                x["samples"],
            ),
            reverse=True,
        )
    return {"min_samples": min_samples, "markets": markets}


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
