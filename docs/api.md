# API contract (v1)

Base path: `/api/v1`. Interactive OpenAPI documentation is available at `/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/power/sample-size` | Estimate two-arm sample size |
| POST | `/experiments/simulate` | Generate seeded binary A/B observations |
| POST | `/experiments/analyze` | Welch t-test, chi-square, or two-proportion z-test |
| POST | `/experiments/multiple-testing` | Bonferroni or Benjamini–Hochberg correction |

## Proportion comparison example

```json
{
  "method": "proportion_z",
  "control": [100, 1000],
  "treatment": [130, 1000],
  "alpha": 0.05
}
```

The arrays are `[successes, total]`, not raw per-user observations.

Schema violations return HTTP 422. Analysis-level invalid inputs should return actionable client errors; unexpected failures must not be turned into fabricated results.


## Advanced endpoints added on the feature branch

### Bayesian binary A/B (Beta-Binomial Monte Carlo)
`POST /api/v1/experiments/bayesian`
```json
{"control_successes":42,"control_total":500,"treatment_successes":58,"treatment_total":500,"prior_alpha":1,"prior_beta":1,"draws":100000,"seed":42}
```
Returns posterior mean conversion rates, the estimated probability treatment conversion exceeds control, and a 95% credible interval for the risk difference. This current implementation uses direct Beta posterior simulation, **not PyMC yet**.

### Sequential binary A/B
`POST /api/v1/experiments/sequential`
```json
{"control_successes":42,"control_total":500,"treatment_successes":58,"treatment_total":500,"alpha":0.05,"looks":5,"current_look":1}
```
Uses a conservative Bonferroni allocation `alpha / looks`. Prespecify the maximum number of looks and do not add looks after observing results. This is a simple fixed-look correction, not a full group-sequential alpha-spending design.

### Causal analysis from CSV text
`POST /api/v1/causal/analyze`
Request includes `csv_text`, `method`, and method-specific column names. Supported methods: `propensity_score_matching`, `difference_in_differences`, `synthetic_control`. The UI upload sends CSV text to `POST /api/v1/data/analyze-csv`; current UI example is a Welch test with `variant` and `converted` columns.

These methods are preliminary implementations. Review the assumptions and caveats returned with every causal estimate; observational methods cannot eliminate unmeasured confounding by themselves.
