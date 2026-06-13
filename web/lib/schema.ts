import { z } from "zod";

export const manifestSchema = z
  .object({
    schema_version: z.literal(2),
    run_id: z.string(),
    git_commit: z.string(),
    data_checksum: z.string(),
    config_checksum: z.string(),
    generated_at: z.string(),
    execution_profile: z.string(),
    canonical: z.boolean(),
    evaluation_mode: z.enum(["held_out", "oof", "simulated"]),
    threshold_policy: z.string(),
    model_versions: z.record(z.string(), z.string()),
    patient_count: z.number().int().nonnegative(),
    active_labels: z.array(z.string()),
    available_evidence: z.array(z.string()),
    warnings: z.array(z.string()),
  })
  .strict();

export const labelDecisionSchema = z.object({
  probability: z.number(),
  threshold: z.number(),
  predicted: z.boolean(),
});

export const patientSchema = z
  .object({
    case_id: z.string(),
    predicted_labels: z.string(),
    conformal_set: z.string(),
    coinfection_prob: z.number(),
    uncertainty_level: z.enum(["low", "moderate", "high"]),
    triage_score: z.number(),
    triage_category: z.enum([
      "Routine Monitoring",
      "Clinical Review",
      "Confirmatory Test Priority",
      "Urgent Response Priority",
    ]),
    recommended_action: z.string(),
    label_decisions: z.record(z.string(), labelDecisionSchema),
    model_track: z.enum(["PRE_LAB", "LAB_AWARE", "FULL"]),
    threshold_policy: z.string(),
    record_source: z.string(),
  })
  .catchall(z.number());

export const summarySchema = z
  .object({
    project: z.string(),
    shape: z.tuple([z.number(), z.number()]),
    active_labels: z.array(z.string()),
    inactive_labels: z.array(z.string()).optional(),
    n_multilabel_patients: z.number().optional(),
    execution_profile: z.string().optional(),
    test_metrics: z.record(z.string(), z.record(z.string(), z.number())),
    calibration_mean_brier: z.number().optional(),
    conformal: z.record(z.string(), z.number()).optional(),
    coinfection: z.record(z.string(), z.union([z.number(), z.string()])).optional(),
    uncertainty_counts: z.record(z.string(), z.number()).optional(),
    triage_distribution: z.record(z.string(), z.number()).optional(),
  })
  .catchall(z.unknown());

const recordSchema = z.record(
  z.string(),
  z.union([z.string(), z.number(), z.boolean(), z.null()]),
);

export const evidenceSchema = z.object({
  model_leaderboard: z.array(recordSchema),
  per_label_metrics: z.array(recordSchema),
  calibration_metrics: z.array(recordSchema),
  conformal_metrics: z.array(recordSchema),
  fairness_metrics: z.array(recordSchema),
  fairness_recall_gaps: z.array(recordSchema),
  center_transfer: z.array(recordSchema),
  feature_importance_global: z.array(recordSchema),
  leakage_candidates: z.array(recordSchema),
  confidence_intervals: z.array(recordSchema),
  label_prevalence_intervals: z.array(recordSchema),
  threshold_policy_tradeoff: z.array(recordSchema),
});

export const patientsSchema = z.array(patientSchema);
