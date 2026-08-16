import math
import numpy as np
from scipy.stats import poisson


def poisson_match(home_xg: float, away_xg: float, max_goals: int = 10):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            matrix[h, a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)

    home = float(np.tril(matrix, -1).sum())
    draw = float(np.trace(matrix))
    away = float(np.triu(matrix, 1).sum())
    over25 = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h + a >= 3))
    btts = float(sum(matrix[h, a] for h in range(max_goals + 1) for a in range(max_goals + 1) if h >= 1 and a >= 1))
    return {
        "home_win": home,
        "draw": draw,
        "away_win": away,
        "over_25": over25,
        "under_25": 1 - over25,
        "btts_yes": btts,
        "btts_no": 1 - btts,
    }


def fair_odds(probability: float) -> float:
    return round(1 / probability, 3) if probability > 0 else math.inf
