import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from io import StringIO

from app.advanced import (bayesian_ab_pymc, sequential_ab, propensity_score_matching, difference_in_differences, synthetic_control, econml_cate, adjust_pvalues)
from app.schemas_advanced import BayesianABRequest, SequentialABRequest, CSVAnalysisRequest, MultipleTestingRequest as AdvancedMultipleTestingRequest

from app.schemas import AnalyzeRequest, MultipleTestingRequest, PowerRequest, SimulationRequest
from app.services import analyze_experiment, correct_pvalues, calculate_sample_size, simulate_ab

app = FastAPI(
    title="Experimentation & Causal Inference API",
    version="0.1.0",
    description="Statistical APIs with explicit assumptions and reproducible outputs.",
)

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://experimentation-and-causal-inference-platform-frontend.vercel.app",
]
configured_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = list(dict.fromkeys(
    default_origins
    + [
        origin.strip().rstrip("/")
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Permit this project's Vercel production and uniquely named deployment URLs.
    # Exact configured origins above remain supported for custom domains.
    allow_origin_regex=r"https://experimentation-and-causal-inference-platform-frontend-[a-z0-9-]+\.vercel\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def invalid_analysis_input(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/", tags=["General"])
def root() -> dict[str, object]:
    """Provide a discoverable landing response for the deployed API."""
    return {
        "name": "Experimentation & Causal Inference Platform",
        "status": "running",
        "message": "API service is online. Use the documentation to explore available endpoints.",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/api/v1/health",
        "available_endpoints": [
            "/api/v1/power/sample-size",
            "/api/v1/experiments/simulate",
            "/api/v1/experiments/analyze",
            "/api/v1/experiments/multiple-testing",
            "/api/v1/experiments/bayesian",
            "/api/v1/experiments/sequential",
            "/api/v1/causal/analyze",
            "/api/v1/data/analyze-csv",
        ],
    }


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "experimentation-causal-platform"}


@app.post("/api/v1/power/sample-size")
def sample_size(request: PowerRequest) -> dict:
    return calculate_sample_size(request)


@app.post("/api/v1/experiments/simulate")
def simulate(request: SimulationRequest) -> dict:
    return simulate_ab(request)


@app.post("/api/v1/experiments/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return analyze_experiment(request)


@app.post("/api/v1/experiments/multiple-testing")
def multiple_testing(request: MultipleTestingRequest) -> dict:
    return correct_pvalues(request)


@app.post("/api/v1/experiments/bayesian")
def bayesian(request: BayesianABRequest) -> dict:
    if request.control_successes > request.control_total or request.treatment_successes > request.treatment_total:
        raise ValueError("Successes cannot exceed totals")
    return bayesian_ab_pymc(**request.model_dump())


@app.post("/api/v1/experiments/sequential")
def sequential(request: SequentialABRequest) -> dict:
    if request.control_successes > request.control_total or request.treatment_successes > request.treatment_total:
        raise ValueError("Successes cannot exceed totals")
    if request.current_look > request.looks:
        raise ValueError("current_look cannot exceed looks")
    return sequential_ab(**request.model_dump())


@app.post("/api/v1/causal/analyze")
def causal_analysis(request: CSVAnalysisRequest) -> dict:
    try:
        data = pd.read_csv(StringIO(request.csv_text))
    except Exception as exc:
        raise ValueError(f"Could not parse CSV: {exc}") from exc
    if data.empty:
        raise ValueError("CSV must contain at least one data row")
    method = request.method
    if method == "econml_cate":
        if not request.treatment_column or not request.outcome_column:
            raise ValueError("treatment_column and outcome_column are required")
        return econml_cate(data, request.treatment_column, request.outcome_column, request.covariate_columns)
    if method == "propensity_score_matching":
        if not request.treatment_column or not request.outcome_column:
            raise ValueError("treatment_column and outcome_column are required")
        return propensity_score_matching(data, request.treatment_column, request.outcome_column, request.covariate_columns)
    if method == "difference_in_differences":
        if not request.group_column or not request.time_column or not request.outcome_column:
            raise ValueError("group_column, time_column (coded 0/1), and outcome_column are required")
        return difference_in_differences(data, request.group_column, request.time_column, request.outcome_column)
    if method == "synthetic_control":
        if not request.group_column or not request.time_column or not request.outcome_column or not request.treated_unit or request.intervention_time is None:
            raise ValueError("group_column (unit), time_column, outcome_column, treated_unit, and intervention_time are required")
        return synthetic_control(data, request.group_column, request.time_column, request.outcome_column, request.treated_unit, request.intervention_time)
    raise ValueError("Unsupported causal method")


@app.post("/api/v1/data/analyze-csv")
def analyze_csv(request: CSVAnalysisRequest) -> dict:
    try:
        data = pd.read_csv(StringIO(request.csv_text))
    except Exception as exc:
        raise ValueError(f"Could not parse CSV: {exc}") from exc
    if data.empty:
        raise ValueError("CSV must contain at least one data row")
    if request.method == "difference_in_differences" or request.method in {"propensity_score_matching", "synthetic_control", "econml_cate"}:
        return causal_analysis(request)
    if request.method == "welch_t":
        if not request.group_column or not request.outcome_column:
            raise ValueError("group_column and outcome_column are required for Welch's t-test")
        groups = list(data[request.group_column].dropna().unique())
        if len(groups) != 2:
            raise ValueError("Selected group column must contain exactly two groups")
        a = pd.to_numeric(data.loc[data[request.group_column] == groups[0], request.outcome_column], errors="coerce").dropna().to_numpy()
        b = pd.to_numeric(data.loc[data[request.group_column] == groups[1], request.outcome_column], errors="coerce").dropna().to_numpy()
        if len(a) < 2 or len(b) < 2:
            raise ValueError("Each group needs at least two numeric outcome values")
        test = __import__("scipy.stats", fromlist=["ttest_ind"]).ttest_ind(b, a, equal_var=False)
        ci = __import__("statsmodels.stats.weightstats", fromlist=["CompareMeans"]).CompareMeans(
            __import__("statsmodels.stats.weightstats", fromlist=["DescrStatsW"]).DescrStatsW(b),
            __import__("statsmodels.stats.weightstats", fromlist=["DescrStatsW"]).DescrStatsW(a)
        ).tconfint_diff(usevar="unequal")
        effect = float(b.mean() - a.mean())
        return {"method":"welch_t", "group_order":[str(groups[0]),str(groups[1])], "sample_sizes":[int(len(a)),int(len(b))],
                "effect_estimate_treatment_minus_control":effect,"p_value":float(test.pvalue),
                "confidence_interval_95":[float(ci[0]),float(ci[1])],
                "interpretation":("Evidence of a difference at alpha=0.05." if test.pvalue < 0.05 else "Insufficient evidence of a difference at alpha=0.05.")}
    raise ValueError("CSV methods supported: welch_t, propensity_score_matching, difference_in_differences, synthetic_control")
