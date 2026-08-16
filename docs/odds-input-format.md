# Historical odds input

CSV columns expected by the value/portfolio layer:

- `date`
- `home_team`
- `away_team`
- `market`
- `market_odds`
- `won`

`market_odds` must be decimal odds greater than 1. `won` is 1 for a winning selection and 0 otherwise. Keep the odds source and timestamp documented separately.

The model must never use post-match information to create the prediction. Odds are only joined to a prediction by match identity and market.
