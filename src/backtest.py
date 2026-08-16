import pandas as pd
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss


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
    p = probs.to_numpy()
    y_valid = y >= 0

    return {
        "samples": int(y_valid.sum()),
        "accuracy": float(accuracy_score(frame.loc[y_valid, "actual"], predicted[y_valid])),
        "log_loss": float(log_loss(y[y_valid], p[y_valid], labels=[0, 1, 2])),
        "brier_multiclass": float(brier_score_brier(y[y_valid], p[y_valid])),
    }


def brier_score_brier(y, probs):
    score = 0.0
    for i, cls in enumerate(y):
        target = (y == cls).astype(float)
        # Multiclass Brier is the mean squared probability-vector error.
        # Compute per row against its one-hot target.
    import numpy as np
    one_hot = np.zeros_like(probs)
    one_hot[np.arange(len(y)), y] = 1
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))
