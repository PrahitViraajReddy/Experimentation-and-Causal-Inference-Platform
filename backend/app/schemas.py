from typing import Literal
from pydantic import BaseModel, Field, model_validator


class PowerRequest(BaseModel):
    metric_type: Literal["continuous", "binary"]
    alpha: float = Field(default=0.05, gt=0, lt=1)
    power: float = Field(default=0.8, gt=0, lt=1)
    allocation_ratio: float = Field(default=1.0, gt=0, le=10)
    standard_deviation: float | None = Field(default=None, gt=0)
    baseline_rate: float | None = Field(default=None, gt=0, lt=1)
    minimum_detectable_effect: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_metric_parameters(self):
        if self.metric_type == "continuous" and self.standard_deviation is None:
            raise ValueError("standard_deviation is required for continuous metrics")
        if self.metric_type == "binary":
            if self.baseline_rate is None:
                raise ValueError("baseline_rate is required for binary metrics")
            if self.baseline_rate + self.minimum_detectable_effect >= 1:
                raise ValueError("baseline_rate + minimum_detectable_effect must be below 1")
        return self


class SimulationRequest(BaseModel):
    sample_size_per_arm: int = Field(default=1000, ge=10, le=1_000_000)
    baseline_rate: float = Field(default=0.10, gt=0, lt=1)
    absolute_effect: float = Field(default=0.02, ge=-0.99, le=0.99)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)

    @model_validator(mode="after")
    def validate_treatment_rate(self):
        if not 0 <= self.baseline_rate + self.absolute_effect <= 1:
            raise ValueError("baseline_rate + absolute_effect must be between 0 and 1")
        return self


class AnalyzeRequest(BaseModel):
    method: Literal["welch_t", "chi_square", "proportion_z"]
    control: list[float | int] = Field(min_length=2, max_length=1_000_000)
    treatment: list[float | int] = Field(min_length=2, max_length=1_000_000)
    alpha: float = Field(default=0.05, gt=0, lt=1)

    @model_validator(mode="after")
    def validate_data(self):
        if any(not isinstance(x, (int, float)) for x in self.control + self.treatment):
            raise ValueError("Observations must be numeric")
        if self.method == "chi_square":
            if any(x < 0 or int(x) != x for x in self.control + self.treatment):
                raise ValueError("chi_square expects non-negative integer category counts")
            if len(self.control) != len(self.treatment):
                raise ValueError("chi_square requires equal-length category count arrays")
        if self.method == "proportion_z":
            for label, values in (("control", self.control), ("treatment", self.treatment)):
                if len(values) != 2 or values[1] <= 0 or not 0 <= values[0] <= values[1]:
                    raise ValueError(f"{label} must be [successes, total]")
                if int(values[0]) != values[0] or int(values[1]) != values[1]:
                    raise ValueError(f"{label} counts must be integers")
        return self


class MultipleTestingRequest(BaseModel):
    p_values: list[float] = Field(min_length=1, max_length=100_000)
    method: Literal["bonferroni", "fdr_bh"]
    alpha: float = Field(default=0.05, gt=0, lt=1)

    @model_validator(mode="after")
    def validate_p_values(self):
        if any(p < 0 or p > 1 for p in self.p_values):
            raise ValueError("p-values must be between 0 and 1")
        return self
