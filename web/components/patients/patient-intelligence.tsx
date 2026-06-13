"use client";

import { Gauge, Layers3, ShieldCheck } from "lucide-react";
import { useState } from "react";

import { ActionRecord } from "@/components/patients/action-record";
import { CaseReport } from "@/components/patients/case-report";
import { DecisionSummary } from "@/components/patients/decision-summary";
import { LabelDecisionList } from "@/components/patients/label-decision-list";
import { PatientSelector } from "@/components/patients/patient-selector";
import { UncertaintyPanel } from "@/components/patients/uncertainty-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { Panel } from "@/components/ui/panel";
import {
  selectRepresentativePatient,
  type RepresentativeScenario,
} from "@/lib/patient-selection";
import type { Manifest, Patient } from "@/lib/types";

export function PatientIntelligence({
  patients,
  manifest,
  initialCaseId,
  initialScenario,
}: {
  patients: Patient[];
  labels: string[];
  manifest: Manifest;
  initialCaseId?: string;
  initialScenario?: RepresentativeScenario;
}) {
  const requestedCase = initialCaseId
    ? patients.find((patient) => patient.case_id === initialCaseId)
    : undefined;
  const scenarioPatient = selectRepresentativePatient(
    patients,
    initialScenario ?? "highest-priority",
  );
  const fallback = scenarioPatient ?? patients[0];

  const [caseId, setCaseId] = useState((requestedCase ?? fallback)?.case_id);
  const [scenario, setScenario] = useState<RepresentativeScenario | null>(
    initialCaseId ? null : (initialScenario ?? "highest-priority"),
  );

  // Unknown-case recovery: a case id was requested but does not exist.
  if (initialCaseId && !requestedCase) {
    return (
      <EmptyState
        title="Case not found"
        description={`No anonymous case matches "${initialCaseId}".`}
        actionHref="/patients?scenario=highest-priority"
        actionLabel="Open highest-priority case"
        icon={<ShieldCheck size={22} />}
      />
    );
  }

  const selected = patients.find((patient) => patient.case_id === caseId) ?? fallback;

  function chooseScenario(value: RepresentativeScenario) {
    const patient = selectRepresentativePatient(patients, value);
    if (patient) {
      setCaseId(patient.case_id);
      setScenario(value);
    }
  }

  function chooseCase(value: string) {
    setCaseId(value);
    setScenario(null);
  }

  return (
    <>
      <Panel
        title="Select a case"
        description="Jump to a representative scenario or pick any anonymous case. Identities are never shown."
        aside={<CaseReport patient={selected} manifest={manifest} />}
      >
        <PatientSelector
          patients={patients}
          selected={selected}
          activeScenario={scenario}
          onScenario={chooseScenario}
          onCase={chooseCase}
        />
      </Panel>

      <DecisionSummary patient={selected} />

      <div className="workspace-grid">
        <div>
          <Panel
            title="Per-disease decisions"
            description="Each calibrated probability is judged against its own tuned threshold (the marker), not a fixed 0.50 cutoff."
            icon={Gauge}
          >
            <LabelDecisionList decisions={selected.label_decisions} />
          </Panel>
          <Panel
            title="Explanation boundary"
            description="The current public artifact contains cohort-level feature importance only."
          >
            <p className="insight">
              Feature contributions describe model behaviour, not medical causality.
              Patient-specific explanations are withheld when they cannot be linked to an
              out-of-fold decision record with sufficient provenance.
            </p>
          </Panel>
        </div>
        <div className="rail">
          <Panel title="Ambiguity & co-infection" description="How sure the model is, and what it keeps in play." icon={Layers3}>
            <UncertaintyPanel patient={selected} />
          </Panel>
          <Panel title="Action record" description="Probability, uncertainty, priority, and action stay distinct.">
            <ActionRecord patient={selected} />
          </Panel>
        </div>
      </div>
    </>
  );
}
