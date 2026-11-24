import type { Step } from "./api";

function time(recordedAt: string): string {
  return new Date(recordedAt).toLocaleTimeString("en-US", {
    hour12: false,
    timeZone: "UTC",
  });
}

/** The agent's steps on a claim, as they happen, with the model cost. */
export function Steps({
  steps,
  working,
}: Readonly<{ steps: Step[]; working: boolean }>) {
  const cost = steps.reduce((total, step) => total + step.cost, 0);
  return (
    <section className="card" aria-labelledby="steps">
      <h2 id="steps">What the agent did, times in UTC</h2>
      {steps.length === 0 && !working && (
        <p className="muted">The agent hasn't worked on this claim.</p>
      )}
      <ol className="steps" aria-live="polite">
        {steps.map((step, index) => (
          <li key={index}>
            <time dateTime={step.recorded_at}>{time(step.recorded_at)}</time>
            <span className="text">{step.text}</span>
            <span className="cost">
              {step.cost > 0 ? `$${step.cost.toFixed(4)}` : ""}
            </span>
          </li>
        ))}
      </ol>
      {working && <p className="working">Working on it</p>}
      {cost > 0 && <p className="mono muted">Model cost ${cost.toFixed(4)}</p>}
    </section>
  );
}
