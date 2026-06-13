import { PageHeader } from "@/components/ui/page-header";
import { SafetyNote } from "@/components/ui/safety-note";

// Stub — the full batch intake workspace is built in Phase 10 (Tasks 15-17).
export default function IntakePage() {
  return (
    <>
      <PageHeader
        title="Batch Intake"
        description="Validate a privacy-safe CSV against the model schema, then run saved-model inference where live inference is available."
        aside={<SafetyNote compact />}
      />
      <div className="panel">
        <p style={{ color: "var(--ink-muted)" }}>
          The batch intake workspace — schema preflight, model-track selection, and
          report export — is being assembled. PRE_LAB is the default deployable track;
          the FULL leakage track is never offered for inference.
        </p>
      </div>
    </>
  );
}
