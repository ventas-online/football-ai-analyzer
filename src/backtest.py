import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, log_loss


def multiclass_brier(y, probs):
    one_hot = np.zeros_like(probs)
    one_hot[np.arange(len(y)), y] = 1
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


def evaluate_1x2(frame: pd.DataFrame):
    """Evaluate frozen pre-match 1X2 predictions.

    Required columns: actual, p_home, p_draw, p_away.
    actual values: H, D, A.
    """
    required = {"actual", "p_home", "p_draw", "p_away"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    probs = frame[["p_home", "p_draw", "p_away"]].clip(1e-6, 1 - 1e-6)
    predicted = probs.idxmax(axis=1).map({"p_home": "H", "p_draw": "D", "p_away": "A"})
    labels = pd.Categorical(frame["actual"], categories=["H", "D", "A"])
    y = labels.codes
    valid = y >= 0
    yv = y[valid]
    pv = probs.to_numpy()[valid]

    return {
        "samples": int(valid.sum()),
        "accuracy": float(accuracy_score(frame.loc[valid, "actual"], predicted[valid])),
        "log_loss": float(log_loss(yv, pv, labels=[0, 1, 2])),
        "brier_multiclass": multiclass_brier(yv, pv),
    }
