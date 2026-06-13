import { readFile } from "node:fs/promises";
import path from "node:path";

import {
  evidenceSchema,
  manifestSchema,
  patientsSchema,
  summarySchema,
} from "@/lib/schema";
import type { DashboardData } from "@/lib/types";

async function readJson(filename: string): Promise<unknown> {
  const file = path.join(process.cwd(), "public", "data", filename);
  return JSON.parse(await readFile(file, "utf-8"));
}

export async function loadDashboardData(): Promise<DashboardData> {
  const [manifest, summary, patients, evidence] = await Promise.all([
    readJson("manifest.json"),
    readJson("summary.json"),
    readJson("patients.json"),
    readJson("evidence.json"),
  ]);
  return {
    manifest: manifestSchema.parse(manifest),
    summary: summarySchema.parse(summary),
    patients: patientsSchema.parse(patients),
    evidence: evidenceSchema.parse(evidence),
  };
}
