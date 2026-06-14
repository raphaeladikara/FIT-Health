export function provenanceText(response) {
  const provenance = response?.provenance || {};
  return `Run ${provenance.run_id || "unknown"} · Policy ${provenance.policy_id || "unavailable"}`;
}
