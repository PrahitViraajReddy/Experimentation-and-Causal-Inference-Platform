# Reference data

This directory documents the platform's reference datasets. Generated CSVs are reproducible and intentionally small; do not commit large third-party raw datasets without checking their license.

## Synthetic randomized A/B dataset

Generate with:

```bash
python scripts/generate_reference_data.py
```

Output: `backend/data/synthetic_ab.csv`

Columns:
- `user_id`: synthetic row identifier (not a real person)
- `variant`: `control` or `treatment`
- `converted`: binary outcome (0/1)
- `revenue`: synthetic non-negative outcome
- `seed`: random seed used to generate the row

The generator uses a fixed seed and known control/treatment conversion probabilities. This is useful for reproducibility and checking whether methods recover a known effect; it is not evidence about a real product.

## Public observational datasets (planned)

The platform's causal-method examples should use documented, openly accessible sources such as the LaLonde NSW job-training data or California Proposition 99 smoking data. Before bundling any raw copy, record the source URL, license/terms, version, treatment, outcome, covariates, and preprocessing. Until those checks are complete, no third-party dataset is claimed to be bundled.
