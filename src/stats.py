from collections import defaultdict


def _empty():
    return {
        "played": 0, "wins": 0, "draws": 0, "losses": 0,
        "goals_for": 0, "goals_against": 0,
        "home_played": 0, "home_goals_for": 0, "home_goals_against": 0,
        "away_played": 0, "away_goals_for": 0, "away_goals_against": 0,
        "recent_matches": [],
    }


def _result(gf, ga):
    return "W" if gf > ga else "L" if gf < ga else "D"


def build_team_stats(matches):
    """Build pre-match-safe aggregate and rolling team statistics."""
    stats = defaultdict(_empty)
    for m in sorted(matches, key=lambda x: x.get("utc_date", "")):
        h, a = m["home_team"], m["away_team"]
        hg, ag = int(m["home_goals"]), int(m["away_goals"])
        hs, ass = stats[h], stats[a]
        hs["played"] += 1; ass["played"] += 1
        hs["goals_for"] += hg; hs["goals_against"] += ag
        ass["goals_for"] += ag; ass["goals_against"] += hg
        hs["home_played"] += 1; hs["home_goals_for"] += hg; hs["home_goals_against"] += ag
        ass["away_played"] += 1; ass["away_goals_for"] += ag; ass["away_goals_against"] += hg
        if hg > ag:
            hs["wins"] += 1; ass["losses"] += 1
        elif hg < ag:
            hs["losses"] += 1; ass["wins"] += 1
        else:
            hs["draws"] += 1; ass["draws"] += 1
        hs["recent_matches"].append({"gf": hg, "ga": ag, "venue": "H", "result": _result(hg, ag)})
        ass["recent_matches"].append({"gf": ag, "ga": hg, "venue": "A", "result": _result(ag, hg)})
        hs["recent_matches"] = hs["recent_matches"][-10:]
        ass["recent_matches"] = ass["recent_matches"][-10:]

    for s in stats.values():
        n = s["played"]
        recent = s["recent_matches"]
        rn = len(recent)
        s["avg_goals_for"] = s["goals_for"] / n if n else 0
        s["avg_goals_against"] = s["goals_against"] / n if n else 0
        s["home_avg_for"] = s["home_goals_for"] / s["home_played"] if s["home_played"] else 0
        s["home_avg_against"] = s["home_goals_against"] / s["home_played"] if s["home_played"] else 0
        s["away_avg_for"] = s["away_goals_for"] / s["away_played"] if s["away_played"] else 0
        s["away_avg_against"] = s["away_goals_against"] / s["away_played"] if s["away_played"] else 0
        s["recent_avg_for"] = sum(x["gf"] for x in recent) / rn if rn else 0
        s["recent_avg_against"] = sum(x["ga"] for x in recent) / rn if rn else 0
        s["recent_points"] = sum(3 if x["result"] == "W" else 1 if x["result"] == "D" else 0 for x in recent)
        s["recent_ppg"] = s["recent_points"] / rn if rn else 0
        s["recent_goal_diff"] = s["recent_avg_for"] - s["recent_avg_against"]
        s["form_sample"] = rn
    return dict(stats)


def estimate_xg(home, away, league_home_avg=1.45, league_away_avg=1.15):
    """Blend season, venue-specific and recent form rates with shrinkage."""
    ha = (home.get("home_avg_for", league_home_avg) + home.get("avg_goals_for", league_home_avg)) / 2
    hd = (home.get("home_avg_against", league_away_avg) + home.get("avg_goals_against", league_away_avg)) / 2
    aa = (away.get("away_avg_for", league_away_avg) + away.get("avg_goals_for", league_away_avg)) / 2
    ad = (away.get("away_avg_against", league_home_avg) + away.get("avg_goals_against", league_home_avg)) / 2
    home_base = (ha + ad) / 2
    away_base = (aa + hd) / 2
    h_weight = 0.30 * min(1.0, home.get("form_sample", 0) / 5)
    a_weight = 0.30 * min(1.0, away.get("form_sample", 0) / 5)
    home_recent = (home.get("recent_avg_for", league_home_avg) + away.get("recent_avg_against", league_away_avg)) / 2
    away_recent = (away.get("recent_avg_for", league_away_avg) + home.get("recent_avg_against", league_home_avg)) / 2
    home_xg = (1 - h_weight) * home_base + h_weight * home_recent
    away_xg = (1 - a_weight) * away_base + a_weight * away_recent
    return max(0.05, min(4.5, home_xg)), max(0.05, min(4.0, away_xg))
