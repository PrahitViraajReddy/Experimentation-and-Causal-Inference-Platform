# Reference datasets

## Cookie Cats randomized A/B test

**Status:** supported download script; raw CSV is downloaded locally on demand and is not committed to this repository.

This dataset contains 90,189 player-level observations from a randomized experiment comparing the location of a progression gate in the Cookie Cats mobile game. It is the first real-data fixture for checking the platform's two-arm analysis methods.

| Column | Meaning |
|---|---|
| `userid` | Unique player identifier |
| `version` | Experiment arm: `gate_30` (control) or `gate_40` (treatment) |
| `sum_gamerounds` | Number of game rounds recorded for the player |
| `retention_1` | Whether the player returned on Day 1 |
| `retention_7` | Whether the player returned on Day 7 |

### Download and validate

From the repository root:

```bash
python scripts/download_reference_data.py
```

The script downloads the CSV into `data/raw/cookie_cats.csv`, then checks the expected columns, 90,189 rows, unique user IDs, both experiment arms, non-negative game-round counts, and boolean retention fields. It refuses to overwrite an existing file and removes incomplete downloads.

### Source and terms

- Original dataset page: [Kaggle — Mobile Games A/B Testing](https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing)
- Download mirror used by the script: [ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats](https://github.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats)
- Raw CSV URL: [cookie_cats.csv](https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv)

The upstream Kaggle page reports an unknown license. This project therefore downloads the file on demand rather than republishing the raw data in its Git history. Review the source terms before redistribution or commercial use. This is a public educational case study, not first-party game telemetry.

### Statistical cautions

- Treat `version` as the randomized assignment and retention fields as binary outcomes.
- Compare Day-1 and Day-7 retention using a two-proportion test or chi-square test; account for multiple comparisons if both are treated as confirmatory outcomes.
- Use `sum_gamerounds` for a continuous-outcome comparison only with a method appropriate to its distribution; it is typically highly skewed.
- Do not treat a small p-value as proof of a practically important effect.
- This dataset is for a randomized experiment, not for demonstrating observational causal methods such as difference-in-differences or synthetic control.

## Planned additional datasets

These are not included or wired into the application yet:
- **LaLonde / NSW job-training data:** candidate observational-treatment case study for matching and treatment-effect estimation.
- **California Proposition 99:** candidate panel-data case study for synthetic control.

They should be added only with documented source, license/terms, data dictionary, and validation checks.
