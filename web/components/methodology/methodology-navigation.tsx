export const METHODOLOGY_SECTIONS: Array<{ id: string; label: string }> = [
  { id: "framing", label: "Multi-label framing" },
  { id: "staging", label: "Feature stages" },
  { id: "validation", label: "Validation" },
  { id: "thresholds", label: "Thresholds" },
  { id: "calibration", label: "Calibration & conformal" },
  { id: "coinfection", label: "Co-infection" },
  { id: "triage", label: "Triage formula" },
  { id: "resources", label: "Resource assumptions" },
  { id: "privacy", label: "Privacy" },
  { id: "provenance", label: "Provenance" },
  { id: "limitations", label: "Limitations" },
  { id: "glossary", label: "Glossary" },
];

export function MethodologyNavigation() {
  return (
    <nav className="method-nav" aria-label="Methodology sections">
      {METHODOLOGY_SECTIONS.map((section) => (
        <a href={`#${section.id}`} key={section.id}>
          {section.label}
        </a>
      ))}
    </nav>
  );
}
