def select_opportunities(markets, market_odds=None, min_probability=0.60, min_edge=0.03):
    """Rank opportunities only when real market odds are supplied.

    Fair odds come from the model. Edge is calculated against supplied odds;
    without odds, the system makes no claim of positive betting value.
    """
    market_odds = market_odds or {}
    candidates = []
    for market, data in markets.items():
        probability = float(data["probability"])
        fair = float(data["fair_odds"])
        odds = market_odds.get(market)
        edge = (probability * float(odds) - 1) if odds and odds > 1 else None
        if probability < min_probability:
            continue
        if edge is not None and edge < min_edge:
            continue
        candidates.append({
            "market": market,
            "probability": probability,
            "fair_odds": fair,
            "market_odds": odds,
            "edge": round(edge, 6) if edge is not None else None,
            "value_status": "VALUE_CHECK_REQUIRED" if edge is None else ("POSITIVE" if edge > 0 else "NEGATIVE"),
        })
    return sorted(candidates, key=lambda x: (x["edge"] is not None, x["edge"] or 0, x["probability"]), reverse=True)
