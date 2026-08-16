from .selection import select_opportunities
from .risk import confidence_label


def generate_signals(prediction, sample_size=0, min_probability=0.60):
    markets = prediction.get("markets", prediction)
    candidates = select_opportunities(markets, min_probability=min_probability)
    signals = []
    for item in candidates:
        edge = item["edge"]
        confidence = confidence_label(item["probability"], sample_size)
        signals.append({
            **item,
            "confidence": confidence,
            "sample_size": sample_size,
            "status": "WATCH" if sample_size < 30 else "CANDIDATE",
        })
    return signals
