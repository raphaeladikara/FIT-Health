import type { Metadata } from "next";

import { GuidedDemo } from "@/components/demo/guided-demo";
import { resolveDemoStep } from "@/lib/demo-steps";
import { loadDashboardData } from "@/lib/data";

export const metadata: Metadata = {
  title: "VECTRA-X guided demo",
  description: "A five-step walkthrough of the VECTRA-X triage argument for judges.",
};

export default async function DemoPage({
  searchParams,
}: {
  searchParams: Promise<{ step?: string }>;
}) {
  const [{ step }, data] = await Promise.all([searchParams, loadDashboardData()]);
  const current = resolveDemoStep(step);
  return <GuidedDemo step={current} data={data} />;
}
