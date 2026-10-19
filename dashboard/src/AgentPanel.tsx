import { useState } from "react";
import type { Claim, Decision } from "./api";
import { api, errorMessage } from "./api";
import { money } from "./format";
import { SignOff } from "./SignOff";

const OUTCOME: Record<Decision["decision"], string> = {
  approve: "Approved",
  decline: "Declined",
  refer: "Referred to a handler",
};

interface Props {
  claim: Claim;
  onChange: () => void;
}

/** The agent's side of a claim: run it, then its decision, payment and sign-off. */
export function AgentPanel({ claim, onChange }: Readonly<Props>) {
  return (
    <section className="panel decision">
      {claim.status === "waiting" && (
        <RunAgent claim={claim} onChange={onChange} />
      )}
      {claim.status === "in_progress" && (
        <p className="working">The agent is working on this claim.</p>
      )}
      {claim.decision && <DecisionView decision={claim.decision} />}
      <Payment claim={claim} onChange={onChange} />
    </section>
  );
}

function RunAgent({ claim, onChange }: Readonly<Props>) {
  const [error, setError] = useState<string>();
  const run = () => {
    api.runAgent(claim.claim_id).then(onChange, (reason: unknown) => {
      setError(errorMessage(reason));
    });
  };
  return (
    <>
      <h2>Not decided yet</h2>
      <p className="muted">The UnderCover Agent hasn't worked this claim.</p>
      <button type="button" className="primary" onClick={run}>
        Run the agent
      </button>
      {error && <p className="error">{error}</p>}
    </>
  );
}

function DecisionView({ decision }: Readonly<{ decision: Decision }>) {
  return (
    <>
      <h2 className={`outcome outcome-${decision.decision}`}>
        {OUTCOME[decision.decision]}
      </h2>
      {decision.decision === "approve" && (
        <p className="payout mono">{money(decision.payout)}</p>
      )}
      <blockquote className="reason">{decision.reason}</blockquote>
      <p className="muted">Policy wording, section {decision.policy_section}</p>
    </>
  );
}

function Payment({ claim, onChange }: Readonly<Props>) {
  if (claim.payment) {
    return (
      <p className="paid">
        Paid <span className="mono">{money(claim.payment.amount)}</span> on{" "}
        <span className="mono">{claim.payment.paid_at.slice(0, 10)}</span>
        {claim.sign_off && (
          <> after sign-off by {claim.sign_off.handler_name}</>
        )}
        .
      </p>
    );
  }
  if (claim.status === "awaiting_signoff") {
    return <SignOff claim={claim} onChange={onChange} />;
  }
  return null;
}
