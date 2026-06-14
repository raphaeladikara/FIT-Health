const SUPPORTED_SCHEMA = "3.0.0";


export function validateRequiredFields(value, fields, label) {
  const missing = fields.filter((field) => value?.[field] === undefined);
  if (missing.length) throw new Error(`${label} missing required fields: ${missing.join(", ")}`);
  return value;
}


export function validateManifest(manifest) {
  if (manifest?.schema_version !== SUPPORTED_SCHEMA) {
    throw new Error(`Unsupported public schema version: ${manifest?.schema_version ?? "missing"}`);
  }
  return validateRequiredFields(
    manifest,
    [
      "notebook_run_id",
      "scientific_schema_version",
      "source_commit",
      "documents",
      "models",
      "policy_ids",
      "class_order",
      "safe_scope",
    ],
    "manifest"
  );
}


export async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return response.json();
}


async function sha256(value) {
  if (!globalThis.crypto?.subtle) return null;
  const canonical = (item) => {
    if (Array.isArray(item)) return `[${item.map(canonical).join(",")}]`;
    if (item && typeof item === "object") {
      return `{${Object.keys(item).sort().map((key) => `${JSON.stringify(key)}:${canonical(item[key])}`).join(",")}}`;
    }
    return JSON.stringify(item);
  };
  const bytes = new TextEncoder().encode(canonical(value));
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}


export async function loadWebBundle() {
  const manifest = validateManifest(await loadJson("data/manifest.json"));
  const [evidence, inputSchema, cases] = await Promise.all([
    loadJson(manifest.documents.evidence.path.replace(/^data\//, "data/")),
    loadJson(manifest.documents.input_schema.path.replace(/^data\//, "data/")),
    loadJson(manifest.documents.demo_cases.path.replace(/^data\//, "data/")),
  ]);
  validateRequiredFields(evidence, ["schema_version", "run_id", "safe_scope"], "evidence");
  validateRequiredFields(inputSchema, ["schema_version", "run_id", "fields"], "input schema");
  if (evidence.run_id !== manifest.notebook_run_id || inputSchema.run_id !== manifest.notebook_run_id) {
    throw new Error("Public bundle run ID mismatch");
  }
  const evidenceHash = await sha256(evidence);
  if (evidenceHash && evidenceHash !== manifest.documents.evidence.sha256) {
    throw new Error("Evidence hash mismatch");
  }
  return { manifest, evidence, inputSchema, cases };
}


export const loadBundle = loadWebBundle;
