# VECTRA-X Full Competition Audit

**Audit date:** 14 June 2026
**Competition deadline in guidebook:** 16 June 2026, 23:59 WIB
**Scope:** repository architecture, raw data, preprocessing, leakage controls,
modeling, evaluation, outputs, notebooks, technical report, dashboard, and FIT
Competition 2026 preliminary-round scoring.

## Executive verdict

VECTRA-X has a stronger concept and broader engineering surface than a typical
competition submission. Its best differentiators are the multi-label framing,
explicit clinical-stage separation, per-label evaluation, uncertainty analysis,
fairness/center-shift audit, and conversion of predictions into a decision-support
story.

However, the current package is not submission-ready. The most serious scientific
issue is an undetected target-restatement feature in the PRE_LAB model:
`Autres maladies presentees par le patient` is transformed into a presence flag.
That flag matches the `other_diseases` target on 98.33% of labeled rows
(94 true positives, 0 false positives, 5 false negatives, 200 true negatives),
with a binary ROC-AUC of approximately 0.9747. It explains an exceptionally large
share of the `other_diseases` prediction and helps produce F1=0.9796. The leakage
screen misses this because it evaluates ordinal category codes while the modeling
pipeline uses missingness/presence.

This means the reported PRE_LAB macro-F1 of 0.6467 and macro-PR-AUC of 0.6078 should
not be used as final competition claims until all artifacts are regenerated after
removing or stage-gating that feature.

There is also an immediate administrative risk: the guidebook asks for a clean
reproducible notebook and a Technical Report PDF. The repository currently contains
three small notebooks, no merged final competition notebook, and no completed final
PDF in `outputs/submission`.

## Estimated score matrix

This is an evidence-based estimate, not an official judge score.

| FIT criterion | Weight | Current estimate | Main reason |
|---|---:|---:|---|
| Visualization and understanding of data | 20 | 14 | Many useful figures and correct multi-label insight, but notebook interpretation is brief and most figures are precomputed |
| Appropriateness of preprocessing | 20 | 8 | Fold-safe imputation is good, but a major semantic target leak remains in PRE_LAB; categorical factorization and missing-target handling are also weak |
| Model performance/evaluation metrics | 20 | 12 | Broad metric coverage, held-out test, OOF selection, calibration and robustness; weakened by leakage, tiny rare-label support, no intervals/repeated validation, and optimistic auxiliary evaluations |
| Introduction/problem/solution/contribution | 10 | 8 | Strong humanitarian framing and clear differentiators |
| Literature review | 10 | 3 | Placeholder bullet list, no in-text citations, incomplete references, little synthesis of related work |
| Methodology | 10 | 6 | Broad and mostly clear, but several statements do not match implementation and key heuristics are not validated |
| Results and discussion | 10 | 6 | Rich results and honest limitations, but some headline conclusions are overstated or internally inconsistent |
| **Estimated technical score** | **100** | **57** | Strong project idea, but scientific and submission blockers materially reduce defensibility |

**Administrative readiness:** currently **not ready**. Missing a final single notebook
and completed PDF can override the technical score through rejection or severe
penalty.

If the P0 and P1 items below are completed well, a realistic target is approximately
**78-86/100**, depending on the leakage-free rerun and the final report quality.

## What the project currently does

1. Loads a 300-row, 109-column bilingual clinical dataset.
2. Detects eight diagnosis columns, retains five labels with positives, and frames
   the task as multi-label.
3. Creates PRE_LAB, LAB_AWARE, and FULL_RESEARCH_ONLY feature tracks.
4. Benchmarks binary-relevance Logistic Regression, Random Forest, Extra Trees,
   HistGradientBoosting, XGBoost, LightGBM, plus supplemental classifier chains.
5. Selects models using 5-fold OOF macro-PR-AUC on a 223-patient training split.
6. Evaluates selected models on a 77-patient held-out test split.
7. Tunes per-label thresholds and reports multi-label and per-label metrics.
8. Adds calibration, label-wise prediction sets, uncertainty categories,
   explainability, subgroup fairness, leave-one-center-out testing, co-infection
   modeling, triage tiers, and resource summaries.
9. Produces 27 tables, 26 figures, 17 reports, two model bundles, three notebooks,
   a local Streamlit tool, and a static public dashboard.

## Critical findings

### P0. PRE_LAB contains a target-restatement leak

The free-text field `Autres maladies presentees par le patient` is non-null for 94
patients. Every one of those 94 patients has the `other_diseases` target, while only
five target-positive patients have the field missing. The preprocessing code turns
this into `<feature>__present`, making it almost a copy of the target.

Why the audit misses it:

- `src/leakage_audit.py` screens high-cardinality text using arbitrary ordinal
  factor codes.
- `src/preprocessing.py` trains on a binary presence indicator.
- The screen and the actual model therefore evaluate different representations.
- The disease-token list does not include `autres`/`other`, so semantic screening
  also misses the target relationship.

Impact:

- `other_diseases` held-out F1 is 0.9796 and PR-AUC is 0.9913.
- Its permutation importance is 0.39608, far larger than other features.
- PRE_LAB macro-F1 and macro-PR-AUC are inflated.
- The claim that PRE_LAB is the "honest deployable model" is currently unsafe.

Required correction:

1. Route this field to `research_only` or remove it entirely.
2. Screen every derived representation, especially missing/presence indicators.
3. Run semantic target-name checks using aliases including `other/autres`.
4. Rebuild all splits, models, metrics, figures, reports, models, and web data.
5. Add an ablation table showing performance with and without every suspicious
   feature.

### P0. The final submission artifacts are missing

The official mechanism requires notebook source and a Technical Report PDF. Current
state:

- Three separate technical notebooks exist.
- No `VECTRA_X_Final_Competition_Notebook.ipynb` exists.
- `outputs/submission` does not contain a completed Technical Report PDF.
- The report is still explicitly marked as a draft and contains cover, table of
  contents, references, and appendix placeholders.

Required correction:

- Produce one top-to-bottom executable competition notebook.
- Produce an A4, formal-English PDF following the official structure and page rules.
- Keep main content within 20 pages, excluding allowed front matter/appendices.
- Use the required filename format: `UNIVERSITY NAME_TEAM NAME`.

### P0. One missing target row is silently converted to an all-negative patient

`label_detection._to_binary` maps missing labels to zero. The raw label columns and
free-text diagnosis have 299 non-null rows, but modeling uses all 300 rows and reports
one patient with no active label.

Impact:

- An unknown target is treated as a confirmed negative for all diseases.
- This affects stratification, training, metrics, and cardinality.

Required correction:

- Verify the row with the competition data dictionary/source.
- Prefer excluding it from supervised evaluation unless "no diagnosis" is explicitly
  confirmed.
- Report the final supervised cohort as n=299 if excluded.

## Evaluation and modeling gaps

### Single split and unstable rare-label estimates

The held-out test contains only 14 dengue, 7 typhoid, and 3 yellow-fever positives.
One prediction changes yellow-fever recall by 33.3 percentage points. Reported
point estimates therefore look more precise than the data supports.

Improve with:

- repeated multi-label stratified CV across at least 10 seeds;
- bootstrap or repeated-CV 95% confidence intervals;
- mean, standard deviation, and interval for macro-F1, macro-PR-AUC, and per-label
  recall/F1;
- a permanently frozen final test set used only once after decisions are locked.

### Missing simple baselines

There is no explicit majority/prevalence baseline, random baseline, or simple
one-rule clinical baseline. Without them, judges cannot see how much value the model
adds over the 90%-malaria prevalence.

Add:

- always-malaria baseline;
- per-label prevalence threshold baseline;
- logistic regression baseline;
- incremental ablation: demographics -> symptoms -> vitals -> labs;
- center-feature and missing-indicator ablations.

### Co-infection result is optimistic

Six models are compared on full-cohort OOF predictions, and the best ROC-AUC is then
reported on those same OOF predictions. This is not an independent estimate after
model selection.

Fix using nested CV or the frozen test set. Report ROC-AUC, PR-AUC, recall,
specificity, and confidence intervals.

### LAB_AWARE does not outperform PRE_LAB on held-out data

Held-out LAB_AWARE macro-F1 is 0.5551 versus PRE_LAB 0.6467, and macro-PR-AUC is
0.5678 versus 0.6078. Any wording that says the lab-aware track scores higher is
contradicted by the current table.

Reframe this as a negative result or rerun same-model paired comparisons with
confidence intervals. Do not imply that adding labs improves performance unless a
paired, leakage-free analysis supports it.

### Model and hyperparameter selection are shallow

Most estimators use one hand-selected parameter set. There is broad model breadth but
limited tuning depth. For a small tabular dataset, carefully regularized models may
beat larger model zoos.

Improve using nested, modest search spaces for:

- Logistic Regression C and penalty;
- Extra Trees depth, leaf size, features, class weighting;
- XGBoost/LightGBM depth, learning rate, regularization, and positive weights;
- label-specific estimators when rare labels need different bias/variance trade-offs.

## Calibration, conformal, and uncertainty gaps

### The implementation is not a conventional dedicated split-conformal procedure

The code fits thresholds using OOF predictions across the entire training set, not a
dedicated untouched calibration split, despite the documentation claiming a
dedicated calibration split. The configured `calibration_size` is not used.

### The quantile cap removes the formal guarantee

The conformal quantile level is capped at 0.90. The code itself acknowledges that this
makes rare-label coverage approximate. Typhoid empirical coverage is only 4/7 =
57.1%, far below the 90% target.

The headline "94.8% coverage" is dominated by common labels and hides:

- typhoid undercoverage;
- 94.81% multi-label ambiguity;
- average set size 2.90 out of five labels;
- yellow fever included for 54/77 patients to cover only three positives.

Improve with:

- a true train/calibration/test design or cross-conformal method with accurate naming;
- exact uncapped results plus an explicitly separate pragmatic policy;
- macro per-label coverage, micro coverage, set size, singleton rate, false-negative
  risk, and coverage-efficiency curves;
- confidence intervals and support beside every coverage value.

### Cohort calibration is in-sample at the calibration layer

The dashboard fits calibrators on cohort OOF predictions and applies them to those
same predictions. Base-model scores are OOF, but calibrated probabilities and all
triage/resource counts are optimistic at the calibration layer.

Use nested cross-fitting: each patient's calibrated probability must come from a
calibrator that did not see that patient's label.

### Uncertainty categories are heuristic

Entropy thresholds 0.50/0.28, max-probability thresholds 0.50/0.78, and set-size
rules are manually chosen and not validated against error rate, selective risk, or
clinical utility.

Add risk-coverage and abstention curves. Show whether "high uncertainty" cases
actually have higher error/FNR than "low uncertainty" cases.

## Explainability, fairness, and operational gaps

### Local "surrogate" explanations do not explain the deployed Extra Trees model

The logistic models are trained directly on ground-truth labels, not on Extra Trees
predictions. They are alternate classifiers, not fidelity-tested surrogates.

Fix by using TreeSHAP for the actual estimator, or fit a local surrogate to the
deployed model's outputs and report local fidelity.

### Fairness values lack denominator context and uncertainty

Several recall gaps of 0.5-1.0 are based on very few positives. The fairness table
shows subgroup n but not per-label positive support or intervals.

Add support, TP/FN, confidence intervals, and an "insufficient evidence" state.
Keep LOCO macro-F1 around 0.37 as the headline generalization warning.

### Center should be ablated

`center_code` is used as a PRE_LAB predictor while center transfer is poor. Compare
with and without center to distinguish useful epidemiological context from site
memorization.

### Triage and resource outputs are not clinically validated

Risk weights, score coefficients, and tier thresholds are manually specified.
Resource "simulation" mainly aggregates predictions and scales demand; it does not
model cost, capacity, waiting time, outcomes, or clinical utility.

Present these as a transparent prototype/scenario projection, not measured impact.
Add sensitivity analysis over weights, thresholds, capacity, and false-negative cost.

## Notebook assessment

Strengths:

- Executed cells are stored and no notebook error outputs were found.
- Project-root bootstrap is robust.
- The three notebooks follow a sensible audit -> modeling -> trust/triage sequence.
- Visual coverage is broad.

Weaknesses:

- Only 19 code cells exist across all three notebooks.
- Many cells only load precomputed CSV/PNG/joblib artifacts.
- The model notebook independently evaluates at threshold 0.5, while the headline
  pipeline uses optimized per-label thresholds.
- There is no unified narrative matching the official report systematics.
- Limited interpretation appears after figures and experiments.
- No confidence intervals, ablation studies, baseline table, or leakage-free rerun.

Best submission structure:

1. Executive abstract and humanitarian problem.
2. Dataset/schema/target audit.
3. Multi-label justification and target support.
4. Missingness and EDA with written insight after every chart.
5. Leakage discovery, including both dengue and other-disease restatements.
6. Leakage-safe preprocessing pipeline.
7. Baselines and experimental protocol.
8. Repeated/nested model comparison.
9. Frozen-test performance with uncertainty intervals.
10. Threshold and error-cost analysis.
11. Calibration and conformal limitations.
12. Explainability of the actual model.
13. Fairness and center-shift analysis.
14. Triage/resource prototype with sensitivity analysis.
15. Limitations, reproducibility, and conclusion.

## Technical report assessment

Strong:

- Clear problem framing and contributions.
- Methodology covers more than the minimum rubric.
- Honest discussion of small data, imbalance, and center shift.
- Good linkage to humanitarian decision support.

Weak:

- It is still a draft, not a final formatted PDF.
- Literature review is a bullet list with no synthesis.
- References are placeholders and there are no proper in-text citations.
- Some methodological wording overstates guarantees or differs from implementation.
- The main report should not lead with metrics contaminated by the other-disease
  restatement.
- Results need confidence intervals, baseline comparisons, and statistical
  uncertainty.

At minimum cite peer-reviewed work for multi-label stratification, classifier chains,
calibration, conformal prediction, explainability, clinical AI fairness, and
domain-shift validation. Use one consistent citation style.

## Prioritized improvement roadmap

### P0: Must finish before submission

1. Remove/stage-gate `Autres maladies presentees par le patient`.
2. Exclude or resolve the row with missing diagnosis targets.
3. Rerun and regenerate every metric/artifact.
4. Build one final executable notebook.
5. Build the final compliant Technical Report PDF.
6. Replace placeholders with team/institution/date/TOC/references.
7. Correct claims about LAB_AWARE and conformal guarantees.

Expected score effect: prevents rejection and restores scientific credibility;
potentially +15 to +25 rubric points relative to the current risky package.

### P1: Highest-value scientific improvements

1. Add baselines and feature-stage ablations.
2. Add repeated/nested multi-label validation and 95% intervals.
3. Independently evaluate co-infection.
4. Use true cross-fitted calibration and accurately named conformal methodology.
5. Add error-cost/threshold curves and selective-risk analysis.

Expected score effect: strongest gain in preprocessing and performance/evaluation,
approximately +8 to +14 points.

### P2: Report and notebook quality

1. Merge into a narrative final notebook.
2. Add interpretation under every figure/table.
3. Add peer-reviewed literature synthesis and consistent citations.
4. Shorten product/dashboard material in the report; prioritize scientific evidence.
5. Add a one-page contribution/novelty table against standard approaches.

Expected score effect: approximately +7 to +12 report/notebook points.

### P3: Presentation differentiators

1. Keep the dashboard as a demo asset, not the core submission evidence.
2. Show one leakage case, one rare-label failure, one uncertainty case, and one
   center-shift result.
3. Present triage/resource outputs as scenario projections.
4. Prepare defense answers for leakage, tiny test support, typhoid coverage, and
   why LAB_AWARE is worse.

## Recommended final competition claims

Safe claims after rerunning:

- The dataset is genuinely multi-label and severely imbalanced.
- Stage-aware feature governance is necessary because diagnostic/restatement fields
  can inflate apparent performance.
- Pre-lab and post-lab models should be evaluated separately.
- Center transfer is substantially weaker than random in-distribution splitting.
- Rare-label performance and uncertainty remain unresolved limitations.

Claims to avoid until fixed:

- PRE_LAB macro-F1=0.6467 as a leakage-free performance figure.
- `other_diseases` F1=0.9796 as genuine predictive performance.
- A formal 90% conformal guarantee.
- 94.8% overall coverage without per-label undercoverage and set-size context.
- Operational or clinical impact from the current triage/resource heuristics.

## Verification performed during this audit

- Read the complete 25-page FIT Competition 2026 Data Science guidebook.
- Inspected all three notebooks, including execution state and stored errors.
- Read the pipeline and all core modeling/evaluation modules.
- Inspected generated summaries, leaderboard, per-label metrics, calibration,
  conformal, fairness, LOCO, resource, and feature-importance tables.
- Verified the `other_diseases` restatement relationship directly from raw data.
- Confirmed 26 figures, 27 tables, 17 reports, and two saved model bundles.
- Ran the static web unit tests: 8 passed, 0 failed.
- Full Python ML rerun was not possible in the available audit runtime because the
  project Python environment is not installed or discoverable from this session.
