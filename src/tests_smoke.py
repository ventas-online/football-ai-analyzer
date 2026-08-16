from .models import poisson_match
from .monte_carlo import simulate
from .value import expected_value
from .selection import select_opportunities


def run():
    p = poisson_match(1.6, 1.1)
    assert abs(p['home_win'] + p['draw'] + p['away_win'] - 1) < 0.02
    mc = simulate(1.6, 1.1, simulations=5000)
    assert 0 <= mc['home_win'] <= 1
    assert expected_value(0.65, 2.0) == 0.3
    signals = select_opportunities({'home_win': {'probability': .7, 'fair_odds': 1/.7}}, .6)
    assert signals
    print('smoke tests passed')


if __name__ == '__main__':
    run()
