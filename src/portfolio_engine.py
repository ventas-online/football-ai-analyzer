from dataclasses import dataclass
from typing import Iterable

@dataclass
class BankrollResult:
    stake: float
    profit: float
    roi: float


def flat_stake(backtest_rows: Iterable[dict], bankroll: float = 1000.0, fraction: float = 0.01) -> BankrollResult:
    stake = bankroll * fraction
    profit = 0.0
    bets = 0
    for row in backtest_rows:
        odds = row.get('market_odds')
        won = row.get('won')
        if odds is None or won is None or odds <= 1:
            continue
        bets += 1
        profit += stake * (odds - 1) if won else -stake
    return BankrollResult(stake, profit, profit / (stake * bets) if bets else 0.0)
