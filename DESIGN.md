# VECTRA-X Design System

## Direction

Presentation-forward clinical decision-support dashboard. The interface combines a
dark navy application shell with high-contrast content surfaces, vivid but controlled
teal and coral accents, polished interactive charts, and restrained state transitions.
It should feel memorable during judging while remaining credible for health-response
workflows.

## Color Strategy

- Background shell: deep navy.
- Primary content surfaces: near-white or dark slate depending on component density.
- Primary accent: teal for selected controls, trusted actions, and normal information.
- Escalation accent: coral/red for urgent states.
- Warning accent: amber for confirmatory-test priority and moderate uncertainty.
- Success accent: green for routine monitoring and sufficient capacity.
- Neutral text and borders must meet WCAG AA contrast.
- Triage categories always combine color with text labels or icons.

## Typography

Use one professional sans-serif family or the system UI stack. Apply a compact product
type scale with clear weight contrast. Reserve large display treatment for the
executive title and major judge-facing claims. Keep controls, tables, and explanations
conventional and highly readable.

## Layout

- Wide static web layout with persistent sidebar navigation.
- Executive overview opens with a concise system statement, metric strip, and three
  high-value interactive charts.
- Detailed pages use a summary-first structure followed by evidence and expandable
  methodology.
- Patient pages use a two-column case workspace: controls and case identity on the
  left, probabilities, triage, uncertainty, and explanations on the right.
- Resource simulation places adjustable assumptions beside capacity and demand
  outcomes so cause and effect remain visible.
- Responsive behavior stacks columns cleanly and keeps tables horizontally usable.

## Components

- Metric cards with restrained surfaces and semantic deltas.
- Plotly charts with consistent disease and triage color mappings.
- Model-mode selector with explicit labels:
  Pre-lab Triage and Lab-aware Confirmation.
- Patient case cards for high confidence, co-infection, high uncertainty, urgent
  priority, and false-negative risk examples.
- Plain-language interpretation panels and technical expanders.
- Static evidence tables, curated anonymous cases, and resource scenarios.
- Clear empty, unavailable, schema-error, and optional-artifact fallback states.

## Motion

Use only subtle 150-250 ms state transitions where supported. Do not animate page
loads or chart content gratuitously. Respect reduced-motion preferences.

## Content Rules

- Use formal English and concise operational language.
- Never label a prediction as a confirmed diagnosis.
- Explain uncertainty and conformal sets in plain language.
- Keep the anonymized-feature causality warning visible in explainability views.
- Clearly distinguish the pre-lab prototype, post-test comparison, and excluded
  target-restating information.

