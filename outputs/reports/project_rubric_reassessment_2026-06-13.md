# VECTRA-X Deep Rubric Reassessment

Date: 13 June 2026

## Executive verdict

VECTRA-X is substantially more thoughtful than a conventional competition
classifier. Its strongest differentiators are the multi-label framing, the
pre-lab/lab-aware distinction, explicit leakage demonstration, broad evaluation,
uncertainty layer, center-transfer stress test, and operational dashboard.

However, the previous internal estimate of about 87/100 is too optimistic for the
current submission artifacts. A strict judge should score what is actually present,
not what the architecture intends to become. The current defensible estimate is:

| Rubric component | Weight | Current score | Weighted score |
|---|---:|---:|---:|
| Visualization and understanding of data | 20 | 16.5/20 | 16.5 |
| Preprocessing appropriateness | 20 | 14.0/20 | 14.0 |
| Model performance and evaluation | 20 | 15.0/20 | 15.0 |
| Introduction, problem, solution, contribution | 10 | 9.0/10 | 9.0 |
| Literature review | 10 | 4.5/10 | 4.5 |
| Methodology | 10 | 7.0/10 | 7.0 |
| Results and discussion | 10 | 7.0/10 | 7.0 |
| **Estimated total** | **100** |  | **73.0/100** |

With the high-priority fixes in this report, an 82-87/100 submission is realistic.
The largest immediate gains are in the report, evaluation uncertainty, and strict
train-only preprocessing rather than dashboard styling.

## 1. Python Notebook (60%)

### 1.1 Visualization and understanding of data: 16.5/20

#### What is strong

- The notebook correctly identifies the task as multi-label. There are 158
  multi-label patients, so a standard multi-class formulation would be wrong.
- It communicates label imbalance, label cardinality, co-occurrence, common
  combinations, missingness, demographics, associations, and a PCA projection.
- EDA is connected to decisions: macro metrics are justified by imbalance,
  conformal sets by overlapping symptoms, and stage-specific models by feature
  availability.
- The notebook is well structured: 66 cells, 45 markdown cells, 21 code cells,
  all 21 code cells executed, and no stored execution errors.
- There are repeated "Key Takeaway" sections, which help judges follow the story.

#### What prevents a higher score

- Several charts describe the cohort but do not quantify uncertainty. With only
  300 rows, prevalence and subgroup bars should include confidence intervals or at
  least counts in every visual.
- Missingness is visualized, but the notebook does not sufficiently test whether
  missingness itself is center-, label-, or workflow-dependent in a way that may
  create shortcut learning.
- The PCA plot has limited inferential value and could be replaced by a more useful
  center-by-label or symptom-by-label comparison with uncertainty.
- The notebook does not clearly distinguish descriptive findings from inferential
  claims. Association plots can be mistaken for clinical relationships.
- The dashboard is impressive but is not part of the displayed 60/40 rubric. It
  should support the notebook, not consume time needed for stronger analysis.

#### Highest-value improvements

1. Add prevalence confidence intervals and support labels to every rare-disease plot.
2. Add missingness-by-center and missingness-by-label statistical summaries.
3. Add a label-prevalence comparison between the two centers.
4. Add one compact "EDA finding -> modeling consequence" table.
5. Replace or demote PCA unless it reveals a defensible pattern.

### 1.2 Appropriateness of preprocessing: 14.0/20

#### What is strong

- Decimal-comma parsing, blood-pressure parsing, yes/no encoding, missing
  indicators, and logged constant removal are appropriate for this dataset.
- Missing values are not silently treated as negative clinical findings.
- Median/constant imputation is placed inside sklearn pipelines.
- Stage-gated feature sets are conceptually excellent and clinically defensible.
- High-cardinality free text is not naively one-hot encoded in a tiny dataset.

#### Critical methodological issue: preprocessing is not fully train-only

The report currently claims leakage-safe preprocessing and "no leakage", but several
decisions are made before the holdout is created:

- `run_pipeline.py` performs target-aware leakage screening on all 300 rows before
  the train/test split is used for modeling.
- Single-feature AUC and mutual information inspect every target, including the
  future test rows, to decide feature routing.
- `make_feature_frame` runs on the full dataset before splitting. Constant removal,
  missing-indicator creation, high-cardinality detection, numeric-vs-categorical
  decisions, and categorical factorization therefore use the test distribution.

This is not the same as directly training on test labels, and the major clinical
stage rules are name-based. Nevertheless, it is transductive preprocessing and
target-informed feature selection. A strict judge can reasonably challenge the
held-out score as not completely untouched.

#### Other preprocessing weaknesses

- `pd.factorize` converts nominal categories to arbitrary integers. Tree models can
  split on these codes as if an order exists.
- Category mappings are not represented as a fitted transformer with an explicit
  unknown-category policy.
- Health center is encoded as one numeric code. With only two centers this works
  numerically, but it encourages center-specific shortcut learning.
- High-cardinality text is reduced to a presence flag, which is safe but discards
  potentially useful symptom information.
- There is no formal comparison of imputation strategies or a preprocessing ablation.
- No batch drift or schema-distribution check is applied before uploaded inference.

#### Highest-value improvements

1. Create the train/test split immediately after label extraction.
2. Fit all data-driven schema and feature-selection decisions on train only.
3. Keep clinical stage routing rule-based; report target statistics as audit evidence,
   not as a test-informed selection mechanism.
4. Replace factorization with `OneHotEncoder(handle_unknown="ignore")` or a documented
   fitted categorical encoder.
5. Add an ablation: no missing indicators vs indicators, center included vs excluded,
   and rule-only vs statistical leakage screening.

### 1.3 Model performance and evaluation metrics: 15.0/20

#### What is strong

- Multi-label stratified splitting is appropriate.
- Six model families plus classifier chain provide a credible benchmark.
- Model selection uses OOF macro PR-AUC, which is appropriate under imbalance.
- The project reports macro, micro, weighted, and samples F1; Hamming loss; subset
  accuracy; Jaccard; per-label precision/recall/F1; ROC-AUC; and PR-AUC.
- Per-label threshold tuning is performed on OOF training predictions, not the test.
- Calibration, co-infection, fairness, explainability, and center transfer broaden
  the evaluation beyond a leaderboard score.
- The honest headline result is reasonable: pre-lab macro F1 0.647, micro F1 0.840,
  macro PR-AUC 0.608, and macro recall 0.725.

#### Main performance limitations

- The test set has only 77 patients. Typhoid has seven test positives and yellow
  fever only three. Point estimates are highly unstable.
- Typhoid remains unsafe: F1 0.308, recall 0.286, and false-negative rate 0.714.
- Yellow-fever F1 0.444 is based on only three positives and should not be presented
  as a stable capability.
- The lab-aware model is not consistently better and completely misses yellow fever
  in the held-out split.
- Leave-one-center-out results are severe: macro F1 is about 0.37-0.38, while recall
  for dengue, typhoid, and yellow fever is 0 at both transferred centers.
- A single fixed holdout is insufficient for a dataset this small. Repeated nested
  evaluation would better estimate variance and model-selection uncertainty.
- OOF leaderboard metrics and held-out threshold-tuned metrics differ substantially.
  These must always be labeled clearly to avoid appearing inconsistent.

#### Calibration and conformal findings need more careful interpretation

- Calibration improves most labels, but malaria and yellow-fever Brier scores become
  slightly worse. The report should say calibration is mixed by label, not uniformly
  better.
- Aggregate conformal coverage is 94.8%, but this hides a major failure:
  typhoid coverage is only 57.1% against a nominal 90% target.
- Yellow-fever coverage is 100%, but the label is included for 54 of 77 patients,
  making the set extremely non-specific.
- Average set size is 2.90 and 94.8% of sets contain multiple labels. This is better
  described as a broad caution/abstention mechanism than a precise conformal result.
- The current implementation calibrates label inclusion from positive examples only.
  Its guarantee should not be described as a general multi-label finite-sample
  coverage guarantee without a more rigorous formulation and validation.

#### Missing evaluation elements

- Bootstrap or repeated-CV confidence intervals.
- Statistical comparison between top models.
- Prevalence or simple-rule baselines for context.
- Decision-curve analysis or net benefit for the triage use case.
- Sensitivity analysis for threshold policies and operational costs.
- Prospective, temporal, or truly external validation.
- An ablation showing whether calibration, conformal logic, and triage layers improve
  a measurable decision objective.

#### Highest-value improvements

1. Add stratified bootstrap 95% confidence intervals for headline and per-label metrics.
2. Add repeated multi-label CV, preferably nested for model/threshold selection.
3. Treat center transfer as a headline limitation, not a secondary fairness result.
4. Report conformal performance per label before aggregate coverage.
5. Add decision-curve/net-benefit analysis for confirmatory-test prioritization.
6. Add a simple prevalence and clinical-rule baseline.

## 2. Technical Report (40%)

### 2.1 Introduction, problem, solution, contribution: 9.0/10

The report has a strong narrative: overlapping symptoms, co-infection, delayed tests,
imbalance, and leakage lead naturally to a staged multi-label triage system. The
contributions are differentiated and relevant to humanitarian operations.

Room for improvement:

- Add one concrete user scenario from intake to confirmatory-test prioritization.
- Define the exact primary endpoint and intended user earlier.
- Avoid "deployable" language. "Competition prototype requiring prospective
  validation" is more defensible.
- Separate scientific contributions from product features.

### 2.2 Literature review: 4.5/10

This is the weakest rubric component. The themes are correct, but the current report
contains a reference placeholder rather than a completed literature review.

Problems:

- No finalized citations or bibliography.
- No structured comparison with related vector-borne disease prediction studies.
- No comparison table covering data size, task type, leakage controls, validation,
  metrics, uncertainty, and deployment setting.
- Claims about WHO/CDC guidance, conformal guarantees, calibration, fairness, and
  multi-label methods are not tied to specific sources.
- The novelty claim is asserted rather than established against prior work.

Highest-value improvements:

1. Finalize 15-25 high-quality references in one citation style.
2. Add a related-work comparison table.
3. State the precise research gap: stage-aware, leakage-audited, multi-label triage
   with uncertainty and operational prioritization on this dataset.
4. Cite primary methodological papers and authoritative clinical guidance.

### 2.3 Methodology: 7.0/10

The methodology is broad and logically organized, but it currently overstates leakage
safety and omits implementation details needed for independent replication.

Required corrections:

- Describe the actual order of split, leakage audit, and preprocessing honestly.
- After refactoring, document every transformer as train-fitted.
- Explain why macro PR-AUC selects the model while macro F1 is the headline.
- Specify hyperparameters or point to a complete table.
- Explain threshold search ranges and objectives.
- Define calibration method selection per label.
- Formalize the conformal nonconformity score and guarantee being claimed.
- Provide equations for uncertainty and triage scores, including risk weights.
- State how fairness subgroup bins are formed and include subgroup support.
- Explain why center is retained as a feature despite poor cross-center transfer.

### 2.4 Results and discussion: 7.0/10

The discussion is honest about leakage and domain shift, but some aggregate claims
remain too favorable.

Required corrections:

- Put typhoid recall 0.286 and center-transfer rare-label recall 0 prominently in the
  main discussion.
- Replace the headline "94.8% conformal coverage" with a per-label table and explain
  typhoid's 57.1% coverage.
- State that calibration is label-dependent and sometimes worsens Brier score.
- Add confidence intervals and test support beside every rare-label result.
- Discuss why lab-aware performance degrades despite added tests.
- Avoid inferring clinical effectiveness from triage-tier distributions; these are
  rule-generated operational outputs, not validated patient outcomes.
- Distinguish model discrimination, calibration, uncertainty, and operational utility.

## 3. Reproducibility and engineering assessment

### Strengths

- Project-relative paths and random state 42 are used.
- The final notebook is executable and has no stored execution errors.
- Full recomputation can be triggered with `VECTRA_X_RECOMPUTE=1`.
- Pipeline artifacts, tables, models, reports, and dashboard data are organized.
- The README documents setup, pipeline execution, notebook execution, and dashboards.

### Weaknesses

- Default notebook execution is artifact-backed, not a full model rebuild. It proves
  rendering and artifact consumption, not end-to-end reproducibility.
- `requirements.txt` uses lower bounds rather than exact pins. Future versions may
  alter metrics or break serialized models.
- Optional XGBoost/LightGBM availability changes the benchmark and potentially the
  selected winner.
- There is no environment lockfile, package snapshot, data checksum, artifact
  manifest, or provenance hash.
- The notebook test checks headings and strings but does not validate values, artifact
  freshness, full recomputation, or model equivalence.
- Cached leaderboard artifacts can become stale relative to code/config/data.
- The current machine does not expose `python` or `py` on the active command path,
  illustrating why launcher/runtime discovery matters.

Recommended additions:

1. Add `requirements-lock.txt` or a reproducible environment file.
2. Save package versions, git commit, data checksum, config checksum, and run timestamp.
3. Add a clean-environment smoke test and a full-pipeline integration test.
4. Mark all tables with source mode: held-out, train OOF, full-cohort OOF, or simulated.
5. Add artifact freshness checks before the notebook reads cached results.

## 4. Privacy, ethics, and deployment limitations

- The raw clinical dataset, model bundles, and `web/data/patients.json` are tracked in
  the repository.
- The static dashboard exposes UUID, true labels, probabilities, conformal sets, and
  triage recommendations to anyone who can access the deployed files.
- UUIDs are pseudonyms, not proof of anonymization. Clinical combinations may still
  be sensitive or re-identifiable.
- Do not publicly deploy patient-level JSON unless the dataset is explicitly approved
  for redistribution and the privacy risk is documented.
- For a public competition demo, use synthetic cases, aggregate-only views, or remove
  UUID and truth labels from the web bundle.
- Triage rules and risk weights are not clinically validated. They are prototype
  decision-support logic, not evidence-based treatment or referral guidance.
- Fairness estimates are too small and unstable to establish equity. They are warning
  diagnostics only.

## 5. Priority roadmap

### P0: before submission

1. Complete the literature review and references.
2. Correct the report's "no leakage" claim and, ideally, refactor preprocessing to be
   train-only.
3. Add confidence intervals and support counts.
4. Rewrite conformal results around per-label performance.
5. Put center-transfer failure and typhoid false negatives in the main limitations.
6. Remove patient-level clinical JSON from any public deployment.
7. Replace cover, table-of-contents, references, and appendix placeholders.

### P1: highest scientific value

1. Repeated/nested multi-label validation.
2. Preprocessing and component ablations.
3. Center-excluded and center-specific models.
4. Decision-curve/net-benefit analysis.
5. Facility-specific recalibration and thresholds.
6. Artifact provenance and locked environment.

### P2: strong next research ideas

1. Hierarchical models that first detect febrile disease/co-infection and then
   discriminate rare labels.
2. Cost-sensitive or focal-loss methods for typhoid and yellow fever.
3. Multi-task or label-dependency models with repeated-CV comparison.
4. Mondrian/group-conditional conformal methods, evaluated per label and center.
5. Drift detection for center, missingness, prevalence, and calibration.
6. Prospective temporal and multi-center validation.
7. Clinician co-design and usability testing with task completion/error measures.
8. Resource optimization based on explicit costs and outcomes rather than heuristic
   triage counts.

## 6. Recommended competition framing

The most defensible story is:

> VECTRA-X is an honest, stage-aware prototype that exposes diagnostic leakage,
> preserves co-infection, and communicates uncertainty. Its current pre-lab model is
> promising in-distribution but not ready for cross-facility clinical use, especially
> for typhoid and other rare labels.

Do not claim:

- deployment readiness;
- validated diagnostic performance;
- uniform calibration improvement;
- reliable 90% conformal coverage for every label;
- fairness;
- generalization to unseen facilities.

Do claim:

- correct multi-label problem formulation;
- explicit feature-availability and leakage reasoning;
- broad, transparent evaluation;
- strong malaria/other-disease discrimination in this sample;
- honest identification of rare-label and center-shift failures;
- a coherent path from model output to human review and resource planning.

## Final assessment

VECTRA-X has a strong competition concept and unusually mature responsible-AI
components, but the current evidence supports a promising prototype, not a validated
clinical system. The best route to a higher score is not more visual polish or more
models. It is stricter experimental isolation, uncertainty intervals, a finished
literature review, honest per-label conformal interpretation, and a sharper discussion
of cross-center failure.
