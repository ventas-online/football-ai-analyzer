# Model v3 — final validation checklist

This checklist defines the gate before the project is considered ready for live personal use.

## Validation gates
- Multi-season chronological walk-forward evaluation
- No future-result leakage
- Baseline comparison
- 1X2, Over 2.5 and BTTS evaluated independently
- Minimum sample size for signal filters
- Calibration gap and Brier/Log Loss reported
- Weak markets/signals automatically excluded
- No claim of profitability without historical market odds
- ROI/edge enabled only when real odds are available
- Final predictions show probability, fair odds, confidence, sample size and model version

## Safety of interpretation
Predictions are statistical estimates, not guarantees. A high model probability is not sufficient evidence of positive expected value. Market odds are required to determine edge and hypothetical ROI.

## Final release gate
Do not label any signal as profitable until it survives out-of-sample testing and has a positive expected-value calculation using real odds from the relevant market.
