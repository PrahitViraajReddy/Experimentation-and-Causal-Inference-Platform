# Statistical methods

## Implemented in this branch
- **Sample-size planning:** independent two-arm, two-sided approximation. Continuous outcome uses standardized mean difference; binary outcome uses Cohen's h approximation. Binary MDE is an absolute risk difference.
- **Welch's t-test:** independent groups, unequal variances allowed; reports treatment-minus-control mean difference and a Welch interval.
- **Chi-square:** two-group category-count table; sparse expected counts need a warning/alternative test before production use.
- **Two-proportion z-test:** input is [successes, total] per group; reports absolute/relative lift and normal-approximation interval.
- **Multiplicity:** Bonferroni family-wise error control and Benjamini–Hochberg false-discovery-rate adjustment.

## Advanced methods available in this branch
- **Sequential testing:** conservative Bonferroni correction across a prespecified maximum number of looks. This is valid only when the look budget and analysis plan are fixed in advance; it is not an information-time alpha-spending design.
- **Bayesian A/B:** PyMC Beta-Binomial MCMC, posterior probability that treatment conversion exceeds control, posterior risk difference, and 95% credible interval. Results depend on the model and priors; inspect sampler diagnostics for consequential use.
- **Propensity-score matching:** DoWhy propensity-score matching with matched-pair and overlap summaries. Identification requires no unmeasured confounding and adequate overlap.
- **Difference-in-differences:** two-by-two design with robust standard errors; relies on parallel trends, no anticipation, and no concurrent treatment-specific shocks.
- **Synthetic control:** nonnegative donor weights fitted on pre-treatment outcomes, pre-treatment RMSE, and post-treatment gaps. Formal inferential p-values are not currently supplied.
- **EconML causal forest:** exploratory average and conditional treatment-effect estimates with confidence interval. Requires adequate overlap and no unmeasured confounding conditional on covariates; validate heterogeneous effects out of sample.

## Interpretation
A p-value is not the probability that the null hypothesis is true. Failure to reject is not proof of equality. Statistical significance does not establish practical value. Causal identification assumptions cannot be proven by one diagnostic.
