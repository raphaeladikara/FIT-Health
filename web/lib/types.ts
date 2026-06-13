export type TriageCategory =
  | "Routine Monitoring"
  | "Clinical Review"
  | "Confirmatory Test Priority"
  | "Urgent Response Priority";

export type UncertaintyLevel = "low" | "moderate" | "high";

export type Patient = {
  case_id: string;
  predicted_labels: string;
  conformal_set: string;
  coinfection_prob: number;
  uncertainty_level: UncertaintyLevel;
  triage_score: number;
  triage_category: TriageCategory;
  recommended_action: string;
  [key: `calprob_${string}`]: number;
};

export type Manifest = {
  schema_version: 1;
  generated_at: string;
  execution_profile: string;
  patient_count: number;
  active_labels: string[];
  available_evidence: string[];
  warnings: string[];
};

export type Summary = {
  project: string;
  shape: [number, number];
  active_labels: string[];
  inactive_labels?: string[];
  n_multilabel_patients?: number;
  execution_profile?: string;
  test_metrics: Record<string, Record<string, number>>;
  calibration_mean_brier?: number;
  conformal?: Record<string, number>;
  coinfection?: Record<string, number | string>;
  uncertainty_counts?: Record<string, number>;
  triage_distribution?: Record<string, number>;
  [key: string]: unknown;
};

export type EvidenceRecord = Record<string, string | number | boolean | null>;

export type Evidence = {
  model_leaderboard: EvidenceRecord[];
  per_label_metrics: EvidenceRecord[];
  calibration_metrics: EvidenceRecord[];
  conformal_metrics: EvidenceRecord[];
  fairness_metrics: EvidenceRecord[];
  fairness_recall_gaps: EvidenceRecord[];
  center_transfer: EvidenceRecord[];
  feature_importance_global: EvidenceRecord[];
  leakage_candidates: EvidenceRecord[];
  confidence_intervals: EvidenceRecord[];
  label_prevalence_intervals: EvidenceRecord[];
  threshold_policy_tradeoff: EvidenceRecord[];
};

export type DashboardData = {
  manifest: Manifest;
  summary: Summary;
  patients: Patient[];
  evidence: Evidence;
};

export type CapacityInput = {
  rapidTests: number;
  beds: number;
  monitoringSlots: number;
  staffReviews: number;
};

export type CapacityRow = {
  resource: "Rapid tests" | "Beds" | "Monitoring slots" | "Staff review slots";
  demand: number;
  capacity: number;
  gap: number;
  status: "Sufficient" | "Insufficient";
};

export type AllocatedPatient = Patient & {
  test_allocation: "Allocated" | "Waiting";
};
