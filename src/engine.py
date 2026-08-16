from .elo import expected_home
from .models import fair_odds, poisson_match
from .monte_carlo import simulate


def analyze_match(home_xg, away_xg, home_elo=1500, away_elo=1500):
    p = poisson_match(home_xg, away_xg)
    mc = simulate(home_xg, away_xg)
    elo_home = expected_home(home_elo, away_elo)

    markets = {
        "home_win": (p["home_win"] + mc["home_win"] + elo_home) / 3,
        "draw": (p["draw"] + mc["draw"]) / 2,
        "away_win": (p["away_win"] + mc["away_win"] + (1 - elo_home)) / 3,
        "over_25": (p["over_25"] + mc["over_25"]) / 2,
        "under_25": p["under_25"],
        "btts_yes": (p["btts_yes"] + mc["btts_yes"]) / 2,
        "btts_no": p["btts_no"],
    }

    total = markets["home_win"] + markets["draw"] + markets["away_win"]
    for key in ("home_win", "draw", "away_win"):
        markets[key] /= total

    return {
        market: {"probability": round(prob, 6), "fair_odds": fair_odds(prob)}
        for market, prob in markets.items()
    }
