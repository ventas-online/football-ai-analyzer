from datetime import datetime, timezone
from .stats import build_team_stats, estimate_xg
from .engine import analyze_match


def prepare_prediction(history, home_team, away_team, elo_home=1500.0, elo_away=1500.0):
    """Generate a prediction using only matches in `history` before the target match."""
    stats = build_team_stats(history)
    if home_team not in stats or away_team not in stats:
        raise ValueError("Both teams need historical matches before prediction")

    home_xg, away_xg = estimate_xg(stats[home_team], stats[away_team])
    result = analyze_match(home_xg, away_xg, home_elo=elo_home, away_elo=elo_away)
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "home_team": home_team,
        "away_team": away_team,
        "home_xg": round(home_xg, 3),
        "away_xg": round(away_xg, 3),
        "elo_home": round(elo_home, 2),
        "elo_away": round(elo_away, 2),
        "markets": result,
        "model_version": "ensemble-v2",
    }
