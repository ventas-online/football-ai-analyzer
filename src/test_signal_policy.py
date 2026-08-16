from .signal_policy import attach_market_odds, rank_signals


def run():
    prediction = {"markets": {
        "home_win": {"probability": 0.68},
        "draw": {"probability": 0.20},
        "away_win": {"probability": 0.12},
        "over_25": {"probability": 0.61},
        "btts_yes": {"probability": 0.59},
    }}
    signals = rank_signals(prediction, sample_size=80)
    assert [x["market"] for x in signals] == ["home_win", "over_25"]
    assert signals[0]["value_status"] == "PENDING_MARKET_ODDS"
    priced = attach_market_odds(signals[0], 1.70)
    assert priced["fair_odds"] > 1.0
    assert priced["theoretical_edge"] > 0
    print("signal policy tests passed")


if __name__ == "__main__":
    run()
