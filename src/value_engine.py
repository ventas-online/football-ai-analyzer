from dataclasses import dataclass
from typing import Optional

@dataclass
class ValueSignal:
    market: str
    probability: float
    fair_odds: float
    market_odds: Optional[float]
    edge: Optional[float]
    ev: Optional[float]
    status: str


def fair_odds(probability: float) -> float:
    if probability <= 0 or probability >= 1:
        raise ValueError('probability must be between 0 and 1')
    return 1.0 / probability


def evaluate(market: str, probability: float, market_odds: Optional[float], min_edge: float = 0.03) -> ValueSignal:
    fair = fair_odds(probability)
    if market_odds is None or market_odds <= 1:
        return ValueSignal(market, probability, fair, market_odds, None, None, 'ODDS_REQUIRED')
    edge = market_odds * probability - 1.0
    ev = edge
    status = 'VALUE_CANDIDATE' if edge >= min_edge else 'NO_VALUE'
    return ValueSignal(market, probability, fair, market_odds, edge, ev, status)
