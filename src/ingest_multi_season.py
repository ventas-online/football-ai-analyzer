import json
import os
import time
from pathlib import Path

from .ingest_football_data import fetch_matches, normalize_matches


DEFAULT_SEASONS = [2022, 2023, 2024, 2025]


def main():
    raw = os.getenv("FOOTBALL_DATA_SEASONS", "2022,2023,2024,2025")
    seasons = [int(x.strip()) for x in raw.split(",") if x.strip()]
    all_rows = []
    seen = set()

    for i, season in enumerate(seasons):
        print(f"Descargando temporada {season} ({i + 1}/{len(seasons)})...")
        data = fetch_matches(status="FINISHED", season=season)
        rows = normalize_matches(data)
        for row in rows:
            row["season"] = season
            if row["external_id"] not in seen:
                seen.add(row["external_id"])
                all_rows.append(row)
        # Stay comfortably below the free API rate limit.
        if i < len(seasons) - 1:
            time.sleep(2)

    all_rows.sort(key=lambda r: r.get("utc_date") or "")
    path = Path("data/raw/matches.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {str(s): sum(1 for r in all_rows if r.get("season") == s) for s in seasons}
    print(f"Total partidos: {len(all_rows)}")
    print(f"Por temporada: {summary}")
    print(f"Guardado en: {path}")


if __name__ == "__main__":
    main()
