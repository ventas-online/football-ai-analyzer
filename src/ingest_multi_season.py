import json
import os
import time
from pathlib import Path

import requests

from .ingest_football_data import fetch_matches, normalize_matches

DEFAULT_SEASONS = [2022, 2023, 2024, 2025]


def main():
    raw = os.getenv("FOOTBALL_DATA_SEASONS", ",".join(map(str, DEFAULT_SEASONS)))
    seasons = [int(x.strip()) for x in raw.split(",") if x.strip()]
    all_rows = []
    seen = set()
    available = []
    skipped = []

    for i, season in enumerate(seasons):
        print(f"Descargando temporada {season} ({i + 1}/{len(seasons)})...")
        try:
            data = fetch_matches(status="FINISHED", season=season)
        except requests.HTTPError as exc:
            response = getattr(exc, "response", None)
            status = getattr(response, "status_code", None)
            if status == 403:
                print(f"Temporada {season} no disponible con el plan actual (HTTP 403). Se omite.")
                skipped.append({"season": season, "reason": "restricted_by_api_plan", "status": 403})
                continue
            raise

        rows = normalize_matches(data)
        available.append(season)
        for row in rows:
            row["season"] = season
            if row["external_id"] not in seen:
                seen.add(row["external_id"])
                all_rows.append(row)

        if i < len(seasons) - 1:
            time.sleep(2)

    if not all_rows:
        raise RuntimeError("La API no devolvió ninguna temporada disponible. Verifica el token y el plan de football-data.org.")

    all_rows.sort(key=lambda r: r.get("utc_date") or "")
    path = Path("data/raw/matches.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {str(s): sum(1 for r in all_rows if r.get("season") == s) for s in available}
    metadata = {
        "requested_seasons": seasons,
        "available_seasons": available,
        "skipped_seasons": skipped,
        "total_matches": len(all_rows),
        "season_match_counts": summary,
    }
    Path("data/raw/ingestion_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Total partidos: {len(all_rows)}")
    print(f"Temporadas disponibles: {available}")
    print(f"Temporadas omitidas: {skipped}")
    print(f"Por temporada: {summary}")
    print(f"Guardado en: {path}")


if __name__ == "__main__":
    main()
