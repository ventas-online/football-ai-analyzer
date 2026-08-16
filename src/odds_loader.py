import csv
from pathlib import Path
from typing import Dict, Tuple

KEY = ('date', 'home_team', 'away_team', 'market')


def load_odds(path: str) -> Dict[Tuple[str, str, str, str], float]:
    """Load normalized historical odds. Missing files are valid and return {}."""
    p = Path(path)
    if not p.exists():
        return {}
    out: Dict[Tuple[str, str, str, str], float] = {}
    with p.open(newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            try:
                key = tuple((r[k] or '').strip() for k in KEY)
                odds = float((r.get('market_odds') or '').strip())
                if all(key) and odds > 1:
                    out[key] = odds
            except (KeyError, TypeError, ValueError):
                continue
    return out
