from collections import defaultdict


def build_team_stats(matches):
    """Build simple pre-match-safe team aggregates from finished matches.

    Each match must contain home_team, away_team, home_goals and away_goals.
    Matches should be ordered chronologically.
    """
    stats = defaultdict(lambda: {
        "played": 0, "wins": 0, "draws": 0, "losses": 0,
        "goals_for": 0, "goals_against": 0,
        "home_played": 0, "home_goals_for": 0, "home_goals_against": 0,
        "away_played": 0, "away_goals_for": 0, "away_goals_against": 0,
        "recent": []
    })

    for m in matches:
        h, a = m["home_team"], m["away_team"]
        hg, ag = int(m["home_goals"]), int(m["away_goals"])
        hs, ass = stats[h], stats[a]

        hs["played"] += 1; ass["played"] += 1
        hs["goals_for"] += hg; hs["goals_against"] += ag
        ass["goals_for"] += ag; ass["goals_against"] += hg
        hs["home_played"] += 1; ass["away_played"] += 1
        hs["home_goals_for"] += hg; hs["home_goals_against"] += ag
        ass["away_goals_for"] += ag; ass["away_goals_against"] += hg

        if hg > ag:
            hs["wins"] += 1; ass["losses"] += 1
            hs["recent"].append("W"); ass["recent"].append("L")
        elif hg < ag:
            hs["losses"] += 1; ass["wins"] += 1
            hs["recent"].append("L"); ass["recent"].append("W")
        else:
            hs["draws"] += 1; ass["draws"] += 1
            hs["recent"].append("D"); ass["recent"].append("D")

        hs["recent"] = hs["recent"][-10:]
        ass["recent"] = ass["recent"][-10:]

    for team, s in stats.items():
        s["avg_goals_for"] = s["goals_for"] / s["played"] if s["played"] else 0
        s["avg_goals_against"] = s["goals_against"] / s["played"] if s["played"] else 0
        s["home_avg_for"] = s["home_goals_for"] / s["home_played"] if s["home_played"] else 0
        s["home_avg_against"] = s["home_goals_against"] / s["home_played"] if s["home_played"] else 0
        s["away_avg_for"] = s["away_goals_for"] / s["away_played"] if s["away_played"] else 0
        s["away_avg_against"] = s["away_goals_against"] / s["away_played"] if s["away_played"] else 0

    return dict(stats)


def estimate_xg(home, away, league_home_avg=1.45, league_away_avg=1.15):
    """Simple transparent xG proxy from scoring/conceding rates.

    This is deliberately conservative until league-specific model fitting exists.
    """
    home_attack = (home.get("home_avg_for", league_home_avg) + home.get("avg_goals_for", league_home_avg)) / 2
    home_defense = (home.get("home_avg_against", league_away_avg) + home.get("avg_goals_against", league_away_avg)) / 2
    away_attack = (away.get("away_avg_for", league_away_avg) + away.get("avg_goals_for", league_away_avg)) / 2
    away_defense = (away.get("away_avg_against", league_home_avg) + away.get("avg_goals_against", league_home_avg)) / 2

    home_xg = (home_attack + away_defense) / 2
    away_xg = (away_attack + home_defense) / 2
    return max(0.05, home_xg), max(0.05, away_xg)
