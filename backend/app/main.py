import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    "https://experimentation-and-causal-inferenc.vercel.app",
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
