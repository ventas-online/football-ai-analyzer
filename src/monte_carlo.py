import numpy as np


def simulate(home_xg, away_xg, simulations=100_000, seed=42):
    rng = np.random.default_rng(seed)
    home = rng.poisson(home_xg, simulations)
    away = rng.poisson(away_xg, simulations)
    return {
        "home_win": float(np.mean(home > away)),
        "draw": float(np.mean(home == away)),
        "away_win": float(np.mean(home < away)),
        "over_25": float(np.mean(home + away >= 3)),
        "btts_yes": float(np.mean((home >= 1) & (away >= 1))),
    }
