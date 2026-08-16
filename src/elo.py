DEFAULT_ELO = 1500.0


def expected_home(elo_home, elo_away, home_advantage=60):
    return 1 / (1 + 10 ** (-(elo_home + home_advantage - elo_away) / 400))


def update(elo_home, elo_away, result_home, k=20, home_advantage=60):
    expected = expected_home(elo_home, elo_away, home_advantage)
    new_home = elo_home + k * (result_home - expected)
    new_away = elo_away + k * ((1 - result_home) - (1 - expected))
    return new_home, new_away
