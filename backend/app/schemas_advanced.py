from typing import Any
from pydantic import BaseModel, Field


class BayesianABRequest(BaseModel):
    control_successes: int = Field(ge=0)
    control_total: int = Field(gt=0)
    treatment_successes: int = Field(ge=0)
    treatment_total: int = Field(gt=0)
    prior_alpha: float = Field(default=1.0, gt=0)
    prior_beta: float = Field(default=1.0, gt=0)
    draws: int = Field(default=1500, ge=500, le=5000)
    seed: int = 42


class SequentialABRequest(BaseModel):
    control_successes: int = Field(ge=0)
    control_total: int = Field(gt=0)
    treatment_successes: int = Field(ge=0)
    treatment_total: int = Field(gt=0)
    alpha: float = Field(default=0.05, gt=0, lt=1)
    looks: int = Field(default=5, ge=1, le=100)
    current_look: int = Field(default=1, ge=1)


class CSVAnalysisRequest(BaseModel):
    csv_text: str
    method: str
    treatment_column: str | None = None
    outcome_column: str | None = None
    covariate_columns: list[str] = Field(default_factory=list)
    group_column: str | None = None
    time_column: str | None = None
    treated_unit: str | None = None
    intervention_time: float | None = None


class MultipleTestingRequest(BaseModel):
    p_values: list[float] = Field(min_length=1, max_length=10000)
    method: str = "fdr_bh"
