from datetime import datetime, timezone
from .stats import build_team_stats, estimate_xg
from .engine import analyze_match


def prepare_prediction(history, home_team, away_team, elo_home=1500.0, elo_away=1500.0):
    """Generate a strictly pre-match prediction plus diagnostics."""
    stats = build_team_stats(history)
    if home_team not in stats or away_team not in stats:
        raise ValueError("Both teams need historical matches before prediction")

    home_stats, away_stats = stats[home_team], stats[away_team]
    home_xg, away_xg = estimate_xg(home_stats, away_stats)
    result = analyze_match(home_xg, away_xg, home_elo=elo_home, away_elo=elo_away)
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "home_team": home_team,
        "away_team": away_team,
        "home_xg": round(home_xg, 3),
        "away_xg": round(away_xg, 3),
        "elo_home": round(elo_home, 2),
        "elo_away": round(elo_away, 2),
        "features": {
            "home_form_ppg": round(home_stats.get("recent_ppg", 0), 3),
            "away_form_ppg": round(away_stats.get("recent_ppg", 0), 3),
            "home_recent_goal_diff": round(home_stats.get("recent_goal_diff", 0), 3),
            "away_recent_goal_diff": round(away_stats.get("recent_goal_diff", 0), 3),
            "home_form_sample": home_stats.get("form_sample", 0),
            "away_form_sample": away_stats.get("form_sample", 0),
        },
        "markets": result,
        "model_version": "ensemble-v3-form-elo-poisson-mc",
    }
