from dataclasses import dataclass
from typing import Iterable

from .data_pipeline import prepare_prediction
from .elo import DEFAULT_ELO, update as update_elo


@dataclass
class BacktestRow:
    home_team: str
    away_team: str
    actual: str
    p_home: float
    p_draw: float
    p_away: float


def walk_forward_predictions(matches: Iterable[dict]):
    """Generate strictly pre-match predictions using a walk-forward history.

    Team ELO ratings are updated only after each completed target match, so
    the target result can never leak into its own prediction.
    """
    ordered = sorted(matches, key=lambda x: x.get("utc_date", ""))
    history = []
    output = []
    elo = {}

    for match in ordered:
        if match.get("home_goals") is None or match.get("away_goals") is None:
            continue

        home = match["home_team"]
        away = match["away_team"]
        seen_teams = set(elo)
        if home in seen_teams and away in seen_teams:
            try:
                pred = prepare_prediction(history, home, away, elo.get(home, DEFAULT_ELO), elo.get(away, DEFAULT_ELO))
                markets = pred["markets"]
                hg, ag = int(match["home_goals"]), int(match["away_goals"])
                actual = "H" if hg > ag else "A" if hg < ag else "D"
                output.append({
                    "external_id": match.get("external_id"),
                    "utc_date": match.get("utc_date"),
                    "home_team": home,
                    "away_team": away,
                    "home_goals": hg,
                    "away_goals": ag,
                    "actual": actual,
                    "p_home": markets["home_win"]["probability"],
                    "p_draw": markets["draw"]["probability"],
                    "p_away": markets["away_win"]["probability"],
                    "p_over_25": markets["over_25"]["probability"],
                    "p_btts_yes": markets["btts_yes"]["probability"],
                    "prediction": pred,
                })
            except ValueError:
                pass

        # Update ELO only after the match has been scored and prediction stored.
        hg, ag = int(match["home_goals"]), int(match["away_goals"])
        result_home = 1.0 if hg > ag else 0.0 if hg < ag else 0.5
        elo[home], elo[away] = update_elo(elo.get(home, DEFAULT_ELO), elo.get(away, DEFAULT_ELO), result_home)
        history.append(match)

    return output
