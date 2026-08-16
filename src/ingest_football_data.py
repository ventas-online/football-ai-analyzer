import os
from pathlib import Path
import json
import requests
from dotenv import load_dotenv

load_dotenv()
BASE = "https://api.football-data.org/v4"
COMPETITION = os.getenv("FOOTBALL_DATA_COMPETITION", "PL")
TOKEN = os.getenv("FOOTBALL_DATA_API_TOKEN", "")


def fetch_matches(date_from=None, date_to=None, status=None, season=None):
    if not TOKEN:
        raise RuntimeError("Falta FOOTBALL_DATA_API_TOKEN en el entorno")
    params = {}
    if date_from: params["dateFrom"] = date_from
    if date_to: params["dateTo"] = date_to
    if status: params["status"] = status
    if season is not None: params["season"] = int(season)
    r = requests.get(
        f"{BASE}/competitions/{COMPETITION}/matches",
        headers={"X-Auth-Token": TOKEN}, params=params, timeout=30
    )
    r.raise_for_status()
    return r.json()


def normalize_matches(data):
    rows = []
    for m in data.get("matches", []):
        score = m.get("score", {}).get("fullTime", {})
        rows.append({
            "external_id": str(m["id"]),
            "utc_date": m.get("utcDate"),
            "status": m.get("status"),
            "home_team": m["homeTeam"]["name"],
            "away_team": m["awayTeam"]["name"],
            "home_goals": score.get("home"),
            "away_goals": score.get("away"),
        })
    return rows


def save_matches_json(data, output="data/raw/matches.json"):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    season = os.getenv("FOOTBALL_DATA_SEASON")
    data = fetch_matches(status="FINISHED", season=season)
    rows = normalize_matches(data)
    path = save_matches_json(rows)
    print(f"Partidos recibidos: {len(rows)}")
    print(f"Guardado en: {path}")
