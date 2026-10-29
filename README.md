# Experimentation & Causal Inference Platform

An analytics platform for planning A/B tests, analyzing experiment outcomes, and estimating treatment effects when randomization is unavailable.



## Scope
- Sample-size / power planning
- Reproducible synthetic A/B data
- Welch's t-test, chi-square, two-proportion z-test
- Bonferroni and Benjamini–Hochberg correction
- Reference data: Cookie Cats randomized A/B test (download-on-demand)
- Roadmap: valid sequential inference, PyMC Bayesian analysis, propensity matching, difference-in-differences, synthetic control

## Stack
React + TypeScript · FastAPI · Pydantic · NumPy · SciPy · Statsmodels · Pytest

## Live deployments
- **Frontend:** https://experimentation-and-causal-inference-platform-fronte-2fmcdq0fy.vercel.app/
- **Backend API:** https://experimentation-and-causal-inference-81xv.onrender.com/
- **Interactive API docs:** https://experimentation-and-causal-inference-81xv.onrender.com/docs

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

## Reference dataset
From the repository root, download and validate the Cookie Cats case study:
```bash
python scripts/download_reference_data.py
```
The script writes `data/raw/cookie_cats.csv` locally and validates its schema and expected 90,189 records. The raw CSV is not committed because the upstream Kaggle listing reports an unknown license. See [dataset provenance, fields, and limitations](docs/datasets.md). Downloading the dataset does not yet mean it is automatically loaded by the application or that all statistical methods have been validated against it.

## Tests
```bash
cd backend
pytest
```


6. Do not publish validation metrics until they have actually been measured.

## Limitations
This is a learning/demo project, not a substitute for statistical review in high-stakes decisions. Bayesian, sequential, and causal methods remain incomplete until their implementations and diagnostics are present and validated.
