# Statistical methods

## Implemented in this branch
- **Sample-size planning:** independent two-arm, two-sided approximation. Continuous outcome uses standardized mean difference; binary outcome uses Cohen's h approximation. Binary MDE is an absolute risk difference.
- **Welch's t-test:** independent groups, unequal variances allowed; reports treatment-minus-control mean difference and a Welch interval.
- **Chi-square:** two-group category-count table; sparse expected counts need a warning/alternative test before production use.
- **Two-proportion z-test:** input is [successes, total] per group; reports absolute/relative lift and normal-approximation interval.
- **Multiplicity:** Bonferroni family-wise error control and Benjamini–Hochberg false-discovery-rate adjustment.

## Planned, not yet implemented
Valid prespecified sequential inference; PyMC Bayesian inference with prior sensitivity checks; propensity-score matching with overlap/balance diagnostics; difference-in-differences with timing and pre-trend diagnostics; synthetic control with pre-treatment fit and placebo diagnostics.

## Interpretation
A p-value is not the probability that the null hypothesis is true. Failure to reject is not proof of equality. Statistical significance does not establish practical value. Causal identification assumptions cannot be proven by one diagnostic.
