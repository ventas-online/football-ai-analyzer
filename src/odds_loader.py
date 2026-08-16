import csv
from pathlib import Path
from typing import Dict, Tuple

KEY = ('date','home_team','away_team','market')

def load_odds(path: str) -> Dict[Tuple[str,str,str,str], float]:
    p = Path(path)
    if not p.exists():
        return {}
    out = {}
    with p.open(newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                key = tuple(r[k].strip() for k in KEY)
                odds = float(r['market_odds'])
                if odds > 1:
                    out[key] = odds
            except (KeyError, ValueError):
                continue
    return out
