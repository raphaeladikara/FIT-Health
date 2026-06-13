# VECTRA-X Final Judge Pitch

## 60-Second Pitch

Vector-borne diseases are difficult to triage because early symptoms overlap,
laboratory tests may be delayed, and one patient may carry multiple diseases.
VECTRA-X is an explainable, uncertainty-aware decision-support system built for that
reality.

Instead of training one classifier on every available column, we first audit when each
feature becomes available. Our main model uses only pre-lab information and achieves
0.65 macro F1, 0.84 micro F1, and 0.73 macro recall. We separately model co-infection,
calibrate confidence, and use conformal prediction to return multiple plausible
diseases when the evidence is ambiguous.

The result is not just a prediction. VECTRA-X assigns transparent triage priorities,
identifies cases needing confirmatory testing or urgent review, and simulates rapid-test,
bed, monitoring, and staff demand through an interactive dashboard.

VECTRA-X does not replace clinicians. It helps them see risk, uncertainty, and resource
needs earlier and more honestly.

## 3-Minute Pitch

### The problem

In endemic settings, fever, headache, nausea, muscle pain, and other symptoms may
indicate malaria, dengue, typhoid, yellow fever, or several diseases at once. Health
workers must decide who can be monitored, who needs a test, and who needs urgent review,
often before laboratory confirmation.

### The data insight

The dataset contains 300 patients and 109 variables. More than half of the patients,
158, have multiple active diagnoses. This means the problem is multi-label, not
multi-class. Malaria is present in 90% of patients, while yellow fever appears in only
12, so accuracy would hide rare-label failure.

### The methodological contribution

We found a second risk: diagnostic leakage. A feature called `Dengue (Dengua)` nearly
restates the dengue outcome. If we use it, the full model looks stronger, but that
performance would not exist before diagnosis. We therefore separate three tracks:
pre-lab triage, lab-aware confirmation, and full-feature research-only.

Our primary pre-lab Extra Trees model reaches 0.647 macro F1, 0.840 micro F1, and
0.725 macro recall. The full model reaches higher apparent performance, but we show
that result only as evidence of leakage awareness.

### The safety and operational layers

VECTRA-X tunes thresholds per disease, calibrates probabilities, estimates uncertainty,
and uses conformal prediction. At 90% target coverage, conformal prediction achieves
about 94.8% empirical coverage. A separate co-infection model reaches 0.863 ROC-AUC.

The dashboard converts these outputs into four triage categories and allows health
teams to simulate rapid-test, bed, monitoring, and staff capacity.

### The conclusion

Our contribution is not simply another classifier. VECTRA-X is a staged,
leakage-aware workflow that reports what is knowable before tests, communicates when it
is uncertain, and turns model outputs into humanitarian response decisions.

## 7-Minute Presentation Flow

### 0:00-0:45, Humanitarian problem

- Overlapping early symptoms.
- Delayed confirmation.
- Co-infection and limited resources.
- Core question: who needs what action first?

### 0:45-1:30, Dataset reality

- 300 patients, 109 variables, two centers.
- 158 multi-label patients.
- Severe imbalance: malaria 90%, yellow fever 4%.
- Accuracy is not an adequate headline metric.

### 1:30-2:30, Leakage reveal

- Show the three feature stages.
- Show `Dengue (Dengua)` as a target-restatement risk.
- Explain why the pre-lab model is the honest primary model.
- Use the full model only to demonstrate inflated performance.

### 2:30-3:30, Model benchmark

- Extra Trees selected for pre-lab triage.
- Pre-lab macro F1 0.647, micro F1 0.840, macro recall 0.725.
- Discuss per-label results and rare-label weakness honestly.
- Present lab-aware as confirmation support.

### 3:30-4:30, Trust and uncertainty

- Threshold policies.
- Calibration and Brier score.
- Conformal coverage 0.948 and average set size 2.90.
- Co-infection ROC-AUC 0.863.
- Explainability warning: statistical signal, not causality.

### 4:30-5:45, Live dashboard demonstration

1. Select an urgent patient.
2. Show disease probabilities, uncertainty, conformal set, and recommended action.
3. Switch to a high-uncertainty case.
4. Upload a small original-schema CSV and run the saved pre-lab model.
5. Download the patient or batch report.

### 5:45-6:30, Resource planning

- Adjust rapid tests, beds, monitoring, and staff.
- Show capacity gaps.
- Compare operational and safety threshold policies.

### 6:30-7:00, Limitations and close

- Small dataset and rare labels.
- Center transfer macro F1 around 0.38.
- Need prospective clinical validation and recalibration.
- Closing line: VECTRA-X helps responders act earlier without pretending the model knows more than the available evidence.

## Strongest Technical Claims

1. The task is correctly modeled as multi-label because 158 of 300 patients have
   multiple active diagnoses.
2. The primary model is leakage-aware and restricted to pre-lab information.
3. Model selection uses multi-label stratified out-of-fold evaluation.
4. Evaluation includes macro and per-label metrics, calibration, uncertainty,
   conformal coverage, fairness, and center transfer.
5. A separate co-infection detector reaches ROC-AUC 0.863.
6. Saved-model CSV inference works without live retraining.
7. The operational layer connects threshold policy to resource demand.

## Strongest Humanitarian Claims

1. The system prioritizes review and confirmation rather than claiming diagnosis.
2. Multi-disease prediction sets communicate ambiguity safely.
3. Co-infection detection supports test and monitoring prioritization.
4. Resource simulation makes model behavior relevant to constrained response settings.
5. The center-shift limitation is disclosed, supporting responsible deployment planning.

## Likely Judge Questions and Ideal Answers

### Why not use accuracy?

Malaria is present in 90% of patients, so a model can appear accurate while failing
rare but important diseases. We prioritize macro F1, macro PR-AUC, recall, and
per-label errors.

### Why is this multi-label rather than multi-class?

Because 158 patients have more than one active diagnosis. A multi-class model would
force one label and discard co-infection.

### Why is the pre-lab model your main model if the full model scores higher?

The full track includes a feature that nearly restates the dengue target. It would not
be available at genuine early triage time. We prefer a lower but honest deployable
score over inflated leakage-driven performance.

### Why does the lab-aware model not always improve?

The available tests mainly confirm the already common malaria label and do not
guarantee better discrimination for every rare disease. Its role is confirmation
support, not automatic superiority.

### Why are conformal sets large?

The dataset is small, malaria is highly prevalent, and symptoms overlap. Broad sets
are an honest representation of ambiguity. They signal when confirmatory testing or
manual review is needed.

### Can this system be deployed now?

No. It is a competition-grade prototype requiring prospective clinical validation,
additional rare-label data, governance, and facility-specific recalibration.

### Are feature explanations medically causal?

No. They explain model behavior. Because features may be anonymized or operationally
encoded, causal interpretation would be inappropriate.

### How do you handle fairness?

We compare subgroup recall and false-negative behavior and perform a leave-one-center-out
stress test. The transfer drop is reported transparently and motivates site-specific
validation.

### What happens when a CSV upload has the wrong schema?

The dashboard validates required columns, reports missing fields, ignores documented
extras, and does not retrain or silently guess.

### What is the single most important contribution?

VECTRA-X aligns model inputs with clinical timing, communicates uncertainty, and
translates predictions into transparent triage and resource decisions.
