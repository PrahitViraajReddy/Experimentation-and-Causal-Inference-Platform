# Statistical foundations

## Hypothesis testing

A test starts with a null hypothesis (for example, equal population means) and an alternative hypothesis (a difference exists). Choose the test and significance level before examining results. A small p-value means the observed data would be unusual under the null model; it is not the probability that the null hypothesis is true and does not measure effect importance.

## Errors, significance, and power

- **Type I error:** reject a true null hypothesis. The significance level `alpha` controls this rate under the test's assumptions.
- **Type II error:** fail to reject a false null hypothesis.
- **Power:** probability of detecting a specified effect when that effect is real; commonly planned at 80% or 90%.
- **Minimum detectable effect (MDE):** smallest effect the experiment is designed to detect at its chosen power and alpha.

Sample-size planning depends on the metric distribution, assignment unit, variance/base rate, allocation, alpha, power, and test assumptions. The calculator's result is an approximation; use a test matching the eventual analysis and account for clustering or repeated measures when present.

## Confidence intervals

A 95% confidence procedure produces intervals that cover the true parameter in 95% of repeated samples under its assumptions. A particular frequentist 95% interval is not a 95% posterior probability statement about the fixed parameter. Report the estimate and interval, not only a significance label.

## Interpretation rules

- Statistical significance does not guarantee practical value.
- A non-significant result does not prove equality.
- Report effect size, uncertainty, sample sizes, test assumptions, and the prespecified alpha.
- Repeatedly checking ordinary p-values while data accumulate can inflate false positives. Use a prespecified sequential design if early stopping is allowed.
- Multiple comparisons require a stated family of hypotheses and an appropriate correction or false-discovery-rate procedure.

## Bayesian probability

Bayesian analysis estimates a posterior distribution conditional on a likelihood and prior. For a conversion metric, a Beta-Binomial model can report `P(p_B > p_A | data)`; the prior and credible interval should be disclosed. A posterior probability is not the same quantity as a frequentist p-value.

## Causal inference cautions

Observational estimates require assumptions. Matching depends on measured confounders and overlap; difference-in-differences depends on a credible parallel-trends assumption; synthetic control depends on a suitable donor pool and pre-treatment fit. Diagnostics and sensitivity/limitations must accompany estimates.
