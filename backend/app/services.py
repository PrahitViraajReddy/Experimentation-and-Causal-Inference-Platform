import math
import numpy as np
from scipy import stats
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest

from app.schemas import AnalyzeRequest, MultipleTestingRequest, PowerRequest, SimulationRequest


def calculate_sample_size(request: PowerRequest) -> dict:
    ratio = request.allocation_ratio
    if request.metric_type == "continuous":
        effect_size = request.minimum_detectable_effect / request.standard_deviation
    else:
        p0 = request.baseline_rate
        p1 = p0 + request.minimum_detectable_effect
        if not 0 < p1 < 1:
            raise ValueError("The target binary rate must be strictly between 0 and 1")
        effect_size = abs(proportion_effectsize(p1, p0))
    n_control_raw = TTestIndPower().solve_power(
        effect_size=effect_size, power=request.power, alpha=request.alpha,
        ratio=ratio, alternative="two-sided"
    )
    n_control = math.ceil(n_control_raw)
    n_treatment = math.ceil(n_control * ratio)
    return {
        "metric_type": request.metric_type,
        "control_sample_size": n_control,
        "treatment_sample_size": n_treatment,
        "total_sample_size": n_control + n_treatment,
        "alpha": request.alpha,
        "target_power": request.power,
        "allocation_ratio": ratio,
        "standardized_effect_size": float(effect_size),
        "method": "two-sided independent two-arm normal approximation",
        "caveat": "Planning estimate; final analysis must match metric, assignment unit, and dependence structure.",
    }


def simulate_ab(request: SimulationRequest) -> dict:
    rng = np.random.default_rng(request.seed)
    n = request.sample_size_per_arm
    p0 = request.baseline_rate
    p1 = p0 + request.absolute_effect
    control = rng.binomial(1, p0, size=n)
    treatment = rng.binomial(1, p1, size=n)
    return {
        "seed": request.seed, "sample_size_per_arm": n,
        "baseline_rate": p0, "treatment_rate": p1,
        "absolute_effect": request.absolute_effect,
        "control": control.tolist(), "treatment": treatment.tolist(),
        "note": "Synthetic independent Bernoulli outcomes; use for reproducibility, not as a real-world benchmark.",
    }


def analyze_experiment(request: AnalyzeRequest) -> dict:
    control = np.asarray(request.control, dtype=float)
    treatment = np.asarray(request.treatment, dtype=float)
    if not np.isfinite(control).all() or not np.isfinite(treatment).all():
        raise ValueError("Observations must all be finite numbers")

    if request.method == "welch_t":
        result = stats.ttest_ind(treatment, control, equal_var=False)
        difference = float(treatment.mean() - control.mean())
        v1, v0 = treatment.var(ddof=1) / len(treatment), control.var(ddof=1) / len(control)
        se = math.sqrt(v1 + v0)
        denominator = v1**2 / (len(treatment) - 1) + v0**2 / (len(control) - 1)
        df = (v1 + v0)**2 / denominator if denominator else float("inf")
        critical = stats.t.ppf(1 - request.alpha / 2, df)
        effect = {"mean_difference_treatment_minus_control": difference,
                  "confidence_interval": [difference - critical * se, difference + critical * se]}
        statistic, p_value = float(result.statistic), float(result.pvalue)
        n_control, n_treatment = len(control), len(treatment)
    elif request.method == "chi_square":
        table = np.vstack([control, treatment])
        if (table.sum(axis=0) == 0).any() or table.sum() == 0:
            raise ValueError("Every category must have a positive combined count")
        result = stats.chi2_contingency(table, correction=False)
        statistic, p_value = float(result.statistic), float(result.pvalue)
        denom = table.sum() * min(table.shape[0] - 1, table.shape[1] - 1)
        effect = {"cramers_v": float(math.sqrt(statistic / denom)) if denom else 0.0}
        n_control, n_treatment = int(control.sum()), int(treatment.sum())
    else:
        counts = np.array([int(treatment[0]), int(control[0])])
        totals = np.array([int(treatment[1]), int(control[1])])
        statistic, p_value = proportions_ztest(counts, totals, alternative="two-sided")
        p_t, p_c = counts[0] / totals[0], counts[1] / totals[1]
        difference = float(p_t - p_c)
        se = math.sqrt(p_t * (1 - p_t) / totals[0] + p_c * (1 - p_c) / totals[1])
        critical = stats.norm.ppf(1 - request.alpha / 2)
        effect = {"treatment_rate": float(p_t), "control_rate": float(p_c),
                  "absolute_lift": difference,
                  "relative_lift": float(difference / p_c) if p_c else None,
                  "confidence_interval": [difference - critical * se, difference + critical * se]}
        statistic, p_value = float(statistic), float(p_value)
        n_control, n_treatment = int(totals[1]), int(totals[0])

    return {
        "method": request.method, "statistic": statistic, "p_value": p_value,
        "alpha": request.alpha, "statistically_significant": bool(p_value < request.alpha),
        "sample_size_control": n_control, "sample_size_treatment": n_treatment, "effect": effect,
        "interpretation": (
            "Statistically significant at the selected alpha; assess effect size and practical importance."
            if p_value < request.alpha else
            "Not statistically significant at the selected alpha; this does not prove the effects are equal."
        ),
    }


def correct_pvalues(request: MultipleTestingRequest) -> dict:
    rejected, adjusted, _, _ = multipletests(
        np.asarray(request.p_values, dtype=float),
        alpha=request.alpha,
        method={"bonferroni": "bonferroni", "fdr_bh": "fdr_bh"}[request.method],
    )
    return {
        "method": request.method, "alpha": request.alpha, "number_of_tests": len(request.p_values),
        "results": [
            {"raw_p_value": float(raw), "adjusted_p_value": float(adj), "reject_null": bool(rej)}
            for raw, adj, rej in zip(request.p_values, adjusted, rejected, strict=True)
        ],
    }
