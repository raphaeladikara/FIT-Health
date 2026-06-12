# VECTRA-X — Presentation Outline (12–15 slides)

*Story arc: this is not a classification problem — it is multi-label triage under
uncertainty, and leakage is the trap most teams will fall into.*

---

**Slide 1 — Title & tagline**
VECTRA-X: A Multi-label, Explainable, Uncertainty-Aware Clinical Triage Intelligence
System for Vector-Borne Disease Response.
*"Prediction is not enough. The model must know when it's uncertain, explain why, and help prioritise action."*

**Slide 2 — The problem (hook)**
Front-line triage of overlapping febrile illnesses, before lab confirmation, under
severe imbalance. Open with: *"The dataset is not a simple classification problem; it
is a multi-label triage problem under uncertainty."*

**Slide 3 — Dataset reality check**
300 × 109, 2 centers. 158/300 patients have >1 diagnosis. Malaria 90%, yellow fever
4%. Three labels have zero positives. → multi-label, imbalance-aware, small-data.
*(figure: target_distribution, label_cardinality)*

**Slide 4 — The leakage trap (differentiator #1)**
*Dengue (Dengua)* AUC ≈ 0.96, *Test TDR* / *Goutte épaisse* near-confirmatory.
Three stage-gated feature sets: PRE_LAB (82) / LAB_AWARE (98) / FULL (99).
*(figure: leakage candidates table)*

**Slide 5 — Two honest scoreboards**
Pre-lab (deployable) vs lab-aware (after tests) vs full (leakage demo). Headline:
*the dramatic gain comes only from the leakage feature* — dengue F1 0.57 → 0.92 in
FULL; genuine lab tests add little. *(figure: model_leaderboard)*

**Slide 6 — Pre-lab model performance**
Extra Trees: macro-F1 0.65, micro-F1 0.84, macro-recall 0.73. Per-label recall &
confusion; malaria recall 1.0 (can't rule out malaria from symptoms → why testing
matters). *(figures: per_label_recall, confusion_matrices)*

**Slide 7 — Co-infection intelligence (differentiator #2)**
Co-infection detector: ROC-AUC 0.86, recall 0.84 from pre-lab features.
Co-occurrence graph: malaria+other, malaria+dengue, malaria+typhoid.
*(figure: label_cooccurrence_heatmap)*

**Slide 8 — Calibration & uncertainty (differentiator #3)**
Reliability curves, Brier ≈ 0.08; patient uncertainty low/moderate/high.
*(figures: calibration_curves, uncertainty_distribution)*

**Slide 9 — Conformal prediction sets (differentiator #4)**
90% target coverage, 94.8% achieved, avg set size 2.9. Example: Patient B →
{Dengue, Typhoid} = "ambiguous, request confirmatory test". The model can abstain.
*(table: conformal_prediction_examples)*

**Slide 10 — Explainability, per stage**
Global + per-label importance; local case studies (confident / uncertain /
co-infection / rare yellow fever). Caveat: anonymised signals, not medical causation.
*(figures: feature_importance_per_label, local_explanation_examples)*

**Slide 11 — Fairness & center robustness (differentiator #5)**
Recall gaps by gender/age/center; leave-one-center-out macro-F1 ≈ 0.38 → honest
generalisation limitation, reported not hidden. *(figure: fairness_recall_gap)*

**Slide 12 — Triage engine & resource impact**
Transparent score → 4 tiers (Routine 66 / Review 87 / Confirmatory 88 / Urgent 59) +
decision-support actions. Resource simulation: how many need testing / urgent review.
*(figures: resource_priority_distribution, threshold_policy_resource_tradeoff)*

**Slide 13 — Live demo (dashboard)**
Patient triage card → probabilities, conformal set, uncertainty, explanation, tier.
Demo script: confident malaria → ambiguous dengue/typhoid → rare yellow-fever sentinel
→ cohort resource panel.

**Slide 14 — Limitations & ethics**
Small n, rare-label uncertainty, center shift, no timestamp/location (external data
supplementary only), decision-support not diagnosis.

**Slide 15 — Conclusion**
Stage-aware multi-label triage that is honest about leakage, calibrated, conformal,
explainable and fair. Deploy pre-lab; confirm with lab-aware; never deploy full.

---

### Demo script (for judges)
1. Confident malaria patient → high-probability single diagnosis (basic function).
2. Dengue/typhoid ambiguous patient → conformal set returns multiple labels →
   "request confirmatory test".
3. Rare yellow-fever sentinel patient → model does not overclaim, escalates review.
4. Cohort resource dashboard → counts needing urgent eval, testing, monitoring.
