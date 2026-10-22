# Assignment Deliverables and Acceptance Checklist

This checklist tracks the complete internship assignment. A feature is complete only after implementation, tests, and documentation are checked; a deployed page alone is not proof of statistical correctness.

## Required implementation

- [ ] **1. Statistical foundations:** document null/alternative hypotheses, p-values, Type I/II errors, statistical power, effect size, and confidence intervals in plain language.
- [ ] **2. FastAPI power/sample-size service:** expose validated API endpoints; document assumptions and test numerical results against known examples.
- [ ] **3. Simulated experiments and frequentist analysis:** generate reproducible A/B data; implement Welch's t-test, chi-square, and multiple-testing correction (Bonferroni and Benjamini–Hochberg); test edge cases and known effects.
- [ ] **4. Safe sequential testing:** implement a documented alpha-spending or another statistically justified sequential design. Do not present repeated ordinary p-value checks as safe peeking.
- [ ] **5. Bayesian A/B analysis with PyMC:** report posterior distributions and the probability that B outperforms A, with prior choices and uncertainty documented.
- [ ] **6. Observational causal methods:** implement propensity-score matching, difference-in-differences, and synthetic control using DoWhy/EconML where appropriate. Include assumptions, diagnostics, and limitations.
- [ ] **7. React data-analysis interface:** support CSV upload, method selection, input validation, plain-English conclusions, and appropriate charts; connect each supported method to the API.

## Required deliverables

- [ ] **Working demo:** deployed end-to-end or a screen recording that demonstrates working flows.
- [ ] **GitHub repository:** clean, meaningful commits; README; reproducible setup instructions.
- [ ] **Architecture and API/data documentation:** architecture diagram, endpoint schemas/examples, dataset provenance, column definitions, and limitations.
- [ ] **Test results:** automated test report plus statistical validation on simulated data with known ground truth; performance numbers where relevant.
- [ ] **10-minute presentation:** problem, design, methods, challenges, results, and next steps.
- [ ] **Individual reflection:** what the intern learned, implemented, and owned.

## Dataset policy

- [ ] Include reproducible, documented reference datasets or scripts that generate reference data.
- [ ] Prefer small, openly licensed/public datasets with source URLs and attribution; keep large/raw datasets out of Git where licensing or repository size makes that inappropriate.
- [ ] Provide a synthetic dataset with known treatment effect for validating statistical methods.
- [ ] Document dataset source, license, target/treatment/outcome columns, preprocessing, and intended method.

## Current status (do not overstate)

The current branch has a starter FastAPI service, initial React interface, initial tests, and basic project documentation. The full assignment is **not yet complete**. Sequential testing, PyMC Bayesian analysis, the three observational causal methods, CSV upload, charts, reference datasets, full statistical validation, presentation, and individual reflection still need implementation and verification.
