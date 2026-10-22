# Deployment guide

This project is configured for a **preview deployment** with a separate static frontend and API service. It is not considered production-ready until CI passes and the deployed smoke tests succeed.

## 1. Deploy the API on Render

The root `render.yaml` defines a web service using the `feat/statistical-platform-foundation` branch. In Render, create a Blueprint from this repository and select that branch. The API service is configured with:
- Build: `pip install -e .`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/v1/health`

After the service deploys, copy its HTTPS URL (for example, `https://your-api.onrender.com`). Confirm `/api/v1/health` returns JSON with `"status": "ok"`.

## 2. Deploy the frontend on Vercel

Import the repository into Vercel and set **Root Directory** to `frontend`. Use the Vite defaults or these settings:
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://your-api.onrender.com`

Replace the example API URL with the real Render URL. Redeploy after setting the variable; Vite embeds `VITE_*` values at build time.

## 3. Configure API CORS

After Vercel gives you the frontend origin, set the Render environment variable:
`CORS_ORIGINS=https://your-frontend.vercel.app`

For multiple origins, use a comma-separated list. Redeploy/restart the API after changing the variable. Do not include paths such as `/search` in CORS origins.

## 4. Verify

1. Open `https://your-api.onrender.com/api/v1/health`.
2. Open the deployed frontend and run a Welch t-test using at least two numeric observations per group.
3. In browser developer tools, confirm the API request succeeds and no CORS error appears.
4. Test the power calculator, proportion test, and multiple-testing endpoint from `/docs`.
5. Check GitHub Actions; both backend tests and frontend build must pass.

## Limitations

- This deployment only exposes the methods currently implemented. Bayesian A/B testing, sequential inference, propensity matching, difference-in-differences, and synthetic control remain unfinished.
- Cookie Cats is downloaded locally by a script; the application does not yet automatically ingest that CSV.
- Do not describe the project as a complete causal-inference platform until the remaining methods, diagnostics, and validation are implemented.
