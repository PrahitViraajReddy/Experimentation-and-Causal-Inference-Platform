# Experimentation & Causal Inference Platform

An internal analytics tool for designing A/B tests, analyzing experiment outcomes, and estimating treatment effects when randomization is unavailable.

**Status:** foundation implementation on a feature branch. Methods are only considered ready when their estimators, diagnostics, and tests are implemented.

## Scope
- Sample-size / power planning
- Reproducible synthetic A/B data
- Welch's t-test, chi-square, two-proportion z-test
- Bonferroni and Benjamini–Hochberg correction
- Roadmap: valid sequential inference, PyMC Bayesian analysis, propensity matching, difference-in-differences, synthetic control

## Stack
React + TypeScript · FastAPI · Pydantic · NumPy · SciPy · Statsmodels · Pytest

## Run locally
Backend (Python 3.11+):
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```
Interactive API docs: http://127.0.0.1:8000/docs

Frontend (Node.js 20+):
```bash
cd frontend
npm install
npm run dev
```
Set `VITE_API_BASE_URL` to override the default API URL.

Tests:
```bash
cd backend
pytest
```

## Statistical integrity
1. Report effect sizes and uncertainty, not only p-values.
2. Statistical significance does not establish practical importance.
3. Failure to reject is not proof of equality.
4. Observational causal estimates depend on assumptions; diagnostics cannot prove them.
5. Repeatedly checking a fixed-horizon p-value is not valid sequential testing.
6. Do not publish validation metrics until they have actually been measured.

## Data strategy
Synthetic A/B data is the ground-truth validation fixture. Cookie Cats is the planned randomized-experiment case study; LaLonde/NSW is the planned observational causal case study. California Proposition 99 is an optional synthetic-control extension. Datasets are not bundled; check source terms before redistribution.

See [architecture](docs/architecture.md) and [statistical methods](docs/statistical-methods.md).

## Limitations
This is a learning/demo project, not a substitute for statistical review in high-stakes decisions. Bayesian, sequential, and causal methods remain incomplete until their implementations and diagnostics are present and validated.
