import type { AgentName } from "./api";
import { api } from "./api";
import { useData } from "./hooks";

const loadQueue = () => api.instructions("queue");
const loadClaim = () => api.instructions("claim");

/** Both agents' instructions, read only. */
export function Instructions() {
  return (
    <>
      <div className="page-head">
        <h1>Agent instructions</h1>
        <span className="muted">Read only</span>
      </div>
      <div className="stack">
        <AgentInstructions title="Queue agent" agent="queue" load={loadQueue} />
        <AgentInstructions title="Claim agent" agent="claim" load={loadClaim} />
      </div>
    </>
  );
}

interface Props {
  title: string;
  agent: AgentName;
  load: () => Promise<string>;
}

function AgentInstructions({ title, agent, load }: Readonly<Props>) {
  const { data, error } = useData(load, 0);
  return (
    <section className="panel" aria-labelledby={`${agent}-instructions`}>
      <h2 id={`${agent}-instructions`}>{title}</h2>
      {error && (
        <p className="error">Couldn't load the instructions: {error}</p>
      )}
      {data && <pre className="instructions">{data}</pre>}
    </section>
  );
}
