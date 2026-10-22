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
