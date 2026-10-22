from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AnalyzeRequest, MultipleTestingRequest, PowerRequest, SimulationRequest
from app.services import analyze_experiment, correct_pvalues, calculate_sample_size, simulate_ab

app = FastAPI(
    title="Experimentation & Causal Inference API",
    version="0.1.0",
    description="Statistical APIs with explicit assumptions and reproducible outputs.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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
