"""Conservative signal ranking for research/personal analysis.

Signals are deliberately not labeled as guaranteed wins. Without market odds,
there is no defensible way to claim positive expected value.
"""

MARKETS = {
    "home_win": "1X2 Home",
    "draw": "1X2 Draw",
    "away_win": "1X2 Away",
    "over_25": "Over 2.5",
    "btts_yes": "BTTS Yes",
}


def _score(probability, sample_size, historical_hit_rate=None):
    """Conservative research score in [0, 100]."""
    p = float(probability)
    sample_factor = min(1.0, max(0.0, sample_size / 100.0))
    if historical_hit_rate is None:
        calibration_factor = 0.65
    else:
        # Reward observed rates near the model probability; penalize large gaps.
        gap = abs(float(historical_hit_rate) - p)
        calibration_factor = max(0.0, 1.0 - 2.5 * gap)
    return round(100.0 * p * (0.45 + 0.35 * sample_factor + 0.20 * calibration_factor), 2)


def rank_signals(prediction, sample_size=0, minimum_probability=0.60):
    """Return ranked research candidates; no market edge is asserted."""
    markets = prediction.get("markets", prediction)
    candidates = []
    for key, label in MARKETS.items():
        item = markets.get(key)
        if not item:
            continue
        probability = float(item.get("probability", 0.0))
        if probability < minimum_probability:
            continue
        candidates.append({
            "market": key,
            "label": label,
            "probability": round(probability, 4),
            "score": _score(probability, sample_size),
            "sample_size": int(sample_size),
            "value_status": "PENDING_MARKET_ODDS",
            "risk_note": "Research signal only; no guaranteed outcome.",
        })
    return sorted(candidates, key=lambda x: x["score"], reverse=True)


def attach_market_odds(signal, decimal_odds):
    """Calculate fair odds and theoretical edge when external odds are supplied."""
    odds = float(decimal_odds)
    p = float(signal["probability"])
    if odds <= 1.0 or p <= 0.0:
        raise ValueError("decimal odds must be > 1 and probability must be > 0")
    fair_odds = 1.0 / p
    edge = p * odds - 1.0
    return {
        **signal,
        "market_odds": round(odds, 4),
        "fair_odds": round(fair_odds, 4),
        "theoretical_edge": round(edge, 4),
        "value_status": "POSITIVE_THEORETICAL_EDGE" if edge > 0 else "NO_THEORETICAL_EDGE",
    }
