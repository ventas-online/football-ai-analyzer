def select_opportunities(markets, min_probability=0.60, min_edge=0.05):
    """Rank statistical opportunities; never labels a pick as guaranteed."""
    candidates = []
    for market, data in markets.items():
        probability = float(data["probability"])
        fair = float(data["fair_odds"])
        if probability < min_probability:
            continue
        candidates.append({
            "market": market,
            "probability": probability,
            "fair_odds": fair,
            "edge": probability - 1 / fair if fair else 0,
        })
    return sorted(candidates, key=lambda x: (x["edge"], x["probability"]), reverse=True)
