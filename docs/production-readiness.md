# Production-readiness gate

## Automated model layer
- Multi-season walk-forward
- Leakage checks
- Baseline comparison
- Calibration diagnostics
- Market-specific signal filtering
- Fair odds / EV engine
- Historical odds ingestion
- Flat-stake ROI engine

## Release requirements
A market can be surfaced as a value candidate only when:
1. The prediction is generated before the match result.
2. The market passes the minimum out-of-sample sample requirement.
3. Calibration diagnostics are acceptable.
4. Real market odds are available.
5. Estimated EV exceeds the configured threshold.

No result is guaranteed. The application is for personal statistical analysis and does not execute wagers automatically.
