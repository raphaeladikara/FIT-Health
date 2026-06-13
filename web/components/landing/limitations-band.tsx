const LIMITATIONS: string[] = [
  "The cohort is small, so headline metrics carry wide confidence intervals.",
  "Rare disease labels have limited support; some recall estimates are unstable.",
  "Center-transfer performance is materially lower than random held-out performance.",
  "This is a research prototype with no prospective clinical or regulatory validation.",
];

export function LimitationsBand() {
  return (
    <section className="landing-section landing-limits" aria-labelledby="limits-heading">
      <h2 id="limits-heading" className="landing-section-title">
        What VECTRA-X cannot claim
      </h2>
      <ul className="limit-list">
        {LIMITATIONS.map((limitation) => (
          <li className="limit-item" key={limitation}>
            {limitation}
          </li>
        ))}
      </ul>
    </section>
  );
}
