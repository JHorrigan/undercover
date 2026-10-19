import { useCallback, useState } from "react";
import { api } from "./api";
import { AgentPanel } from "./AgentPanel";
import { Evidence } from "./Evidence";
import { humanize } from "./format";
import { useData } from "./hooks";
import { SectionsRead } from "./SectionsRead";
import { StatusBadge } from "./Status";
import { Steps } from "./Steps";

const LIVE_MS = 2000;

export function ClaimPage({ id }: Readonly<{ id: string }>) {
  const [started, setStarted] = useState(false);
  const loadClaim = useCallback(() => api.claim(id), [id]);
  const loadSteps = useCallback(() => api.steps(id), [id]);
  const [live, setLive] = useState(false);
  const claim = useData(loadClaim, live ? LIVE_MS : 0);
  const steps = useData(loadSteps, live ? LIVE_MS : 0);
  const status = claim.data?.status;
  const working = status === "in_progress" || (started && status === "waiting");
  if (working !== live) setLive(working);

  const onChange = () => {
    setStarted(true);
    claim.reload();
    steps.reload();
  };

  if (claim.error) return <p className="error">{claim.error}</p>;
  if (!claim.data) return <p className="muted">Loading the claim.</p>;
  return (
    <>
      <a className="back" href="#/">
        Back to the queue
      </a>
      <div className="page-head">
        <div>
          <h1>{claim.data.summary}</h1>
          <p className="muted">
            <span className="mono">{claim.data.claim_id}</span>,{" "}
            {humanize(claim.data.claim_type)}
          </p>
        </div>
        <StatusBadge status={claim.data.status} />
      </div>
      <div className="claim-layout">
        <Evidence claim={claim.data} />
        <div className="stack agent-side">
          <AgentPanel claim={claim.data} onChange={onChange} />
          <SectionsRead steps={steps.data ?? []} />
          <Steps steps={steps.data ?? []} />
        </div>
      </div>
    </>
  );
}
