from dataclasses import dataclass
from typing import Iterable

from .data_pipeline import prepare_prediction


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

    The target match is never included in the history used to predict it.
    """
    ordered = sorted(matches, key=lambda x: x.get("utc_date", ""))
    history = []
    output = []

    for match in ordered:
        if match.get("home_goals") is None or match.get("away_goals") is None:
            continue

        home = match["home_team"]
        away = match["away_team"]
        if home in {x["home_team"] for x in history} or home in {x["away_team"] for x in history}:
            try:
                pred = prepare_prediction(history, home, away)
                markets = pred["markets"]
                actual = "H" if match["home_goals"] > match["away_goals"] else "A" if match["home_goals"] < match["away_goals"] else "D"
                output.append({
                    "external_id": match.get("external_id"),
                    "utc_date": match.get("utc_date"),
                    "home_team": home,
                    "away_team": away,
                    "actual": actual,
                    "p_home": markets["home_win"]["probability"],
                    "p_draw": markets["draw"]["probability"],
                    "p_away": markets["away_win"]["probability"],
                    "prediction": pred,
                })
            except ValueError:
                pass

        history.append(match)

    return output
