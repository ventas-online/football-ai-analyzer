def implied_probability(odds: float) -> float:
    return 1 / odds if odds and odds > 1 else 0.0


def expected_value(probability: float, odds: float) -> float:
    """Expected profit per 1 unit staked, before commission/taxes."""
    return probability * odds - 1 if odds and odds > 1 else 0.0


def value_report(probability: float, odds: float):
    ev = expected_value(probability, odds)
    return {
        "model_probability": probability,
        "market_probability": implied_probability(odds),
        "fair_odds": round(1 / probability, 3) if probability > 0 else None,
        "expected_value": round(ev, 6),
        "has_value": ev > 0,
    }
