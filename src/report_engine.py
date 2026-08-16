from collections import defaultdict
from typing import Iterable


def summarize_signals(rows: Iterable[dict]) -> dict:
    groups = defaultdict(lambda: {'n': 0, 'wins': 0, 'profit': 0.0, 'bets': 0})
    for r in rows:
        market = r.get('market', 'unknown')
        status = r.get('status', 'UNKNOWN')
        g = groups[(market, status)]
        g['n'] += 1
        if r.get('won') is not None:
            g['bets'] += 1
            if r['won']:
                g['wins'] += 1
            if r.get('market_odds') and r['market_odds'] > 1:
                g['profit'] += r['market_odds'] - 1 if r['won'] else -1
    out = []
    for (market, status), g in groups.items():
        out.append({**g, 'market': market, 'status': status,
                    'hit_rate': g['wins'] / g['bets'] if g['bets'] else None,
                    'roi': g['profit'] / g['bets'] if g['bets'] else None})
    return sorted(out, key=lambda x: (x['roi'] is not None, x['roi'] or -999), reverse=True)
