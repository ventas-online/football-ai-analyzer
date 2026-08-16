# Final architecture

The personal football analyzer is organized into five layers:

1. **Data** — historical results and metadata from free sources available to the account.
2. **Features** — rolling form, home/away splits, goals, ELO, Poisson and simulation features computed only from information available before each match.
3. **Model** — ensemble probabilities for 1X2, Over 2.5 and BTTS, evaluated with chronological walk-forward validation and calibration diagnostics.
4. **Value** — fair odds, market odds, edge and expected value. No value claim is made when market odds are absent.
5. **Portfolio** — conservative flat-stake backtest, ROI and profit tracking when historical odds are supplied.

## Signal lifecycle

PREDICTION -> CALIBRATION -> FAIR ODDS -> MARKET ODDS -> EDGE/EV -> FILTER -> PORTFOLIO BACKTEST -> FINAL RANKING

Signals are informational statistical estimates, not guarantees. A prediction is not treated as a positive-value wager without market odds.
