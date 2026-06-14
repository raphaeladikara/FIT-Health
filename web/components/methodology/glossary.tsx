import { GLOSSARY } from "@/lib/glossary";

export function Glossary() {
  return (
    <section className="prose-section" id="glossary">
      <h2>Glossary</h2>
      <dl className="glossary-list">
        {Object.entries(GLOSSARY).map(([slug, entry]) => (
          <div className="glossary-item" id={`glossary-${slug}`} key={slug}>
            <dt>{entry.term}</dt>
            <dd>{entry.definition}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
