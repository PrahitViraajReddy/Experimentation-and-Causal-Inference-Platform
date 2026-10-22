"""Advanced statistical methods for the Experimentation & Causal Inference Platform."""
from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import linear_sum_assignment
from scipy.special import expit
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint


def bayesian_ab(control_successes: int, control_total: int, treatment_successes: int, treatment_total: int,
                prior_alpha: float = 1.0, prior_beta: float = 1.0, draws: int = 100_000, seed: int = 42) -> dict[str, Any]:
    """Beta-Binomial posterior for conversion; reports P(treatment > control)."""
    for successes, total, label in ((control_successes, control_total, "control"), (treatment_successes, treatment_total, "treatment")):
        if total <= 0 or successes < 0 or successes > total:
            raise ValueError(f"{label} requires 0 <= successes <= total and total > 0")
    if prior_alpha <= 0 or prior_beta <= 0 or draws < 1000:
        raise ValueError("Prior parameters must be positive and draws must be >= 1000")
    rng = np.random.default_rng(seed)
    a = rng.beta(prior_alpha + control_successes, prior_beta + control_total - control_successes, draws)
    b = rng.beta(prior_alpha + treatment_successes, prior_beta + treatment_total - treatment_successes, draws)
    delta = b - a
    return {"method": "bayesian_beta_binomial", "probability_treatment_better": float(np.mean(delta > 0)),
            "control_posterior_mean": float((prior_alpha + control_successes) / (prior_alpha + prior_beta + control_total)),
            "treatment_posterior_mean": float((prior_alpha + treatment_successes) / (prior_alpha + prior_beta + treatment_total)),
            "risk_difference_mean": float(np.mean(delta)),
            "risk_difference_credible_interval_95": [float(x) for x in np.quantile(delta, [0.025, 0.975])],
            "draws": draws, "seed": seed,
            "note": "Monte Carlo Beta-Binomial model with Beta prior; probability is conditional on this model and prior."}


def sequential_ab(control_successes: int, control_total: int, treatment_successes: int, treatment_total: int,
                  alpha: float = 0.05, looks: int = 5, current_look: int | None = None) -> dict[str, Any]:
    """Conservative Bonferroni alpha-spending across a prespecified number of looks."""
    if looks < 1 or not 0 < alpha < 1:
        raise ValueError("looks must be >= 1 and alpha must be between 0 and 1")
    if current_look is None:
        current_look = looks
    if not 1 <= current_look <= looks:
        raise ValueError("current_look must be between 1 and looks")
    for successes, total, label in ((control_successes, control_total, "control"), (treatment_successes, treatment_total, "treatment")):
        if total <= 0 or successes < 0 or successes > total:
            raise ValueError(f"{label} requires 0 <= successes <= total and total > 0")
    p1, p2 = control_successes / control_total, treatment_successes / treatment_total
    pooled = (control_successes + treatment_successes) / (control_total + treatment_total)
    se = np.sqrt(pooled * (1 - pooled) * (1 / control_total + 1 / treatment_total))
    z = (p2 - p1) / se if se > 0 else 0.0
    p = float(2 * stats.norm.sf(abs(z)))
    adjusted_alpha = alpha / looks
    return {"method": "bonferroni_sequential_proportion_test", "p_value": p, "z_statistic": float(z),
            "nominal_alpha": alpha, "planned_looks": looks, "current_look": current_look,
            "per_look_alpha": adjusted_alpha, "reject_null_at_this_look": bool(p < adjusted_alpha),
            "stop_for_significance": bool(p < adjusted_alpha), "note": "Conservative Bonferroni correction controls family-wise error across at most the prespecified number of looks. Use fixed look schedule and do not add looks after seeing results."}


def _require_columns(data: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def propensity_score_matching(data: pd.DataFrame, treatment: str, outcome: str, covariates: list[str]) -> dict[str, Any]:
    """1:1 nearest propensity-score matching without replacement; binary treatment."""
    _require_columns(data, [treatment, outcome, *covariates])
    frame = data[[treatment, outcome, *covariates]].dropna().copy()
    if not covariates or len(frame) < 10 or set(frame[treatment].unique()) != {0, 1}:
        raise ValueError("Need >=10 complete rows, covariates, and binary treatment coded 0/1 with both groups present")
    x = pd.get_dummies(frame[covariates], drop_first=True, dtype=float)
    x = x.replace([np.inf, -np.inf], np.nan)
    if x.isna().any().any():
        raise ValueError("Covariates must be numeric/categorical and finite after encoding")
    x = (x - x.mean()) / x.std(ddof=0).replace(0, 1)
    # Logistic propensity model, fitted with a small ridge penalty for stability.
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(C=1.0, max_iter=2000, random_state=42)
    t = frame[treatment].astype(int).to_numpy()
    model.fit(x, t)
    ps = np.clip(model.predict_proba(x)[:, 1], 1e-6, 1 - 1e-6)
    treated_idx, control_idx = np.flatnonzero(t == 1), np.flatnonzero(t == 0)
    cost = np.abs(ps[treated_idx, None] - ps[control_idx][None, :])
    rows, cols = linear_sum_assignment(cost)
    distances = cost[rows, cols]
    caliper = 0.2 * float(np.std(np.log(ps / (1 - ps)), ddof=1))
    keep = distances <= caliper if caliper > 0 else np.ones_like(distances, dtype=bool)
    ti, ci = treated_idx[rows[keep]], control_idx[cols[keep]]
    if len(ti) < 2:
        raise ValueError("Too few matched pairs within the propensity-score caliper; check overlap and covariates")
    differences = frame[outcome].to_numpy()[ti].astype(float) - frame[outcome].to_numpy()[ci].astype(float)
    se = float(stats.sem(differences))
    ci95 = stats.t.interval(0.95, len(differences)-1, loc=float(np.mean(differences)), scale=se) if se > 0 else (float(np.mean(differences)), float(np.mean(differences)))
    return {"method":"propensity_score_matching", "estimand":"ATT among matched treated units",
            "effect_estimate":float(np.mean(differences)), "confidence_interval_95":[float(ci95[0]),float(ci95[1])],
            "matched_pairs":int(len(differences)), "treated_rows":int(len(treated_idx)), "control_rows":int(len(control_idx)),
            "caliper_logit_sd":caliper, "propensity_score_range":[float(ps.min()),float(ps.max())],
            "caveat":"Associational identification requires no unmeasured confounding, adequate overlap, and correctly measured covariates. Review balance before causal interpretation."}


def difference_in_differences(data: pd.DataFrame, treatment_group: str, post_period: str, outcome: str) -> dict[str, Any]:
    """Two-by-two DiD from group (0/1), period (0/1), and numeric outcome."""
    _require_columns(data, [treatment_group, post_period, outcome])
    frame = data[[treatment_group, post_period, outcome]].dropna().copy()
    if set(frame[treatment_group].unique()) != {0,1} or set(frame[post_period].unique()) != {0,1}:
        raise ValueError("Group and period must each be coded 0/1 and contain both values")
    frame[outcome] = pd.to_numeric(frame[outcome], errors="raise")
    means = frame.groupby([treatment_group, post_period])[outcome].mean()
    needed = [(0,0),(0,1),(1,0),(1,1)]
    if any(k not in means.index for k in needed):
        raise ValueError("All four group-period cells must contain observations")
    effect = float((means.loc[(1,1)] - means.loc[(1,0)]) - (means.loc[(0,1)] - means.loc[(0,0)]))
    # OLS interaction with HC1 robust standard errors.
    import statsmodels.formula.api as smf
    fit = smf.ols(f"{outcome} ~ {treatment_group} * {post_period}", data=frame).fit(cov_type="HC1")
    term = f"{treatment_group}:{post_period}"
    if term not in fit.params.index:
        term = f"{post_period}:{treatment_group}"
    ci = fit.conf_int().loc[term].tolist()
    return {"method":"difference_in_differences", "effect_estimate":effect,
            "confidence_interval_95":[float(ci[0]),float(ci[1])], "p_value":float(fit.pvalues[term]),
            "cell_means":{"control_pre":float(means.loc[(0,0)]),"control_post":float(means.loc[(0,1)]),"treated_pre":float(means.loc[(1,0)]),"treated_post":float(means.loc[(1,1)])},
            "caveat":"Causal interpretation relies on parallel trends, no anticipation, stable group composition, and no concurrent treatment-specific shocks."}


def synthetic_control(data: pd.DataFrame, unit: str, time: str, outcome: str, treated_unit: str, intervention_time: Any) -> dict[str, Any]:
    """Simple non-negative donor-weight synthetic control; weights fit on pre-treatment outcomes."""
    _require_columns(data, [unit, time, outcome])
    frame = data[[unit,time,outcome]].dropna().copy()
    frame[outcome] = pd.to_numeric(frame[outcome], errors="raise")
    frame[time] = pd.to_numeric(frame[time], errors="raise")
    if treated_unit not in set(frame[unit]):
        raise ValueError("treated_unit not found")
    pre = sorted(frame.loc[frame[time] < float(intervention_time), time].unique())
    post = sorted(frame.loc[frame[time] >= float(intervention_time), time].unique())
    if len(pre) < 2 or not post:
        raise ValueError("Need at least two pre-intervention periods and one post-intervention period")
    pivot = frame.pivot_table(index=time, columns=unit, values=outcome, aggfunc="mean")
    donors = [u for u in pivot.columns if u != treated_unit]
    usable = [u for u in donors if pivot.loc[pre, [u]].notna().all().all() and pivot.loc[post, [u]].notna().all().all()]
    if not usable or pivot.loc[pre, [treated_unit]].isna().any().any() or pivot.loc[post, [treated_unit]].isna().any().any():
        raise ValueError("Need complete pre/post outcomes for treated unit and at least one donor")
    target = pivot.loc[pre, treated_unit].to_numpy(float)
    matrix = pivot.loc[pre, usable].to_numpy(float)
    # Projected-gradient fit for nonnegative weights summing to one.
    weights = np.full(len(usable), 1/len(usable))
    lipschitz = max(float(np.linalg.norm(matrix.T @ matrix, 2)), 1e-8)
    step = 1 / lipschitz
    for _ in range(5000):
        candidate = weights - step * (matrix.T @ (matrix @ weights - target))
        # Euclidean projection onto probability simplex.
        u = np.sort(candidate)[::-1]; cssv = np.cumsum(u) - 1
        rho = np.flatnonzero(u - cssv / (np.arange(len(u)) + 1) > 0)
        theta = cssv[rho[-1]] / (rho[-1] + 1) if len(rho) else 0
        new_weights = np.maximum(candidate - theta, 0)
        if np.linalg.norm(new_weights - weights) < 1e-10: weights = new_weights; break
        weights = new_weights
    actual = pivot.loc[post, treated_unit].to_numpy(float)
    synthetic = pivot.loc[post, usable].to_numpy(float) @ weights
    gaps = actual - synthetic
    pre_synthetic = matrix @ weights
    pre_rmse = float(np.sqrt(np.mean((target-pre_synthetic)**2)))
    return {"method":"synthetic_control", "treated_unit":str(treated_unit), "intervention_time":intervention_time,
            "post_period_average_effect":float(np.mean(gaps)), "post_period_gaps":[float(x) for x in gaps],
            "donor_weights":{str(k):float(v) for k,v in zip(usable,weights)}, "pre_treatment_rmse":pre_rmse,
            "pre_periods":len(pre),"post_periods":len(post),
            "caveat":"Descriptive synthetic-control estimate; inference is not supplied. Check pre-fit, donor contamination, placebo units/times, and sensitivity before causal claims."}


def adjust_pvalues(p_values: list[float], method: str = "fdr_bh") -> dict[str, Any]:
    if not p_values or any(not np.isfinite(p) or p < 0 or p > 1 for p in p_values):
        raise ValueError("Provide p-values in [0, 1]")
    if method not in {"bonferroni","fdr_bh"}:
        raise ValueError("method must be bonferroni or fdr_bh")
    reject, adjusted, _, _ = multipletests(p_values, method=method)
    return {"method":method,"adjusted_p_values":[float(x) for x in adjusted],"reject_at_0_05":[bool(x) for x in reject]}
