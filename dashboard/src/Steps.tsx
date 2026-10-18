import type { Step } from "./api";

const KIND_LABEL: Record<Step["kind"], string> = {
  tool: "Called",
  result: "Got back",
  reply: "Said",
};

/** The agent's steps on a claim, in order. */
export function Steps({ steps }: Readonly<{ steps: Step[] }>) {
  return (
    <section className="panel" aria-live="polite">
      <h2>What the agent did</h2>
      {steps.length === 0 && (
        <p className="muted">The agent's steps appear here as it works.</p>
      )}
      <ol className="steps">
        {steps.map((step) => (
          <li key={step.id} className={`step step-${step.kind}`}>
            <span className="muted">{KIND_LABEL[step.kind]}</span>
            <span className="step-text">{step.text}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
