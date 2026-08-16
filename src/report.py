from collections import Counter


def summarize_predictions(rows):
    """Summarize model predictions without pretending they are guaranteed bets."""
    if not rows:
        return {"samples": 0, "accuracy": None, "markets": {}}

    correct = 0
    for row in rows:
        probs = {"H": row["p_home"], "D": row["p_draw"], "A": row["p_away"]}
        if max(probs, key=probs.get) == row["actual"]:
            correct += 1

    return {
        "samples": len(rows),
        "accuracy": correct / len(rows),
        "actual_distribution": dict(Counter(r["actual"] for r in rows)),
    }
