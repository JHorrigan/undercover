import type { Step } from "./api";

/** The sections of the policy wording and the claims manual the agent read. */
export function SectionsRead({ steps }: Readonly<{ steps: Step[] }>) {
  const reads = steps.filter((step) => step.kind === "read");
  if (reads.length === 0) return null;
  return (
    <section className="panel">
      <h2>What the agent read</h2>
      <ul className="sections-read">
        {reads.map((step) => (
          <li key={step.id}>{step.text}</li>
        ))}
      </ul>
    </section>
  );
}
