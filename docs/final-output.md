# Final report output

The application should expose one consolidated report with:

- model version and data coverage;
- out-of-sample sample size;
- baseline comparison;
- market-level hit rate, Brier and Log Loss;
- calibration by probability bucket;
- signal filter status;
- fair odds;
- market odds when available;
- edge and expected value;
- number of qualifying bets;
- flat-stake profit and ROI;
- drawdown when bankroll series is available;
- final signal ranking.

Missing odds must produce `ODDS_REQUIRED`, never a fabricated ROI.
