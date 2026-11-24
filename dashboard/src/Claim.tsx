import { useCallback } from "react";
import { api, type Claim as ClaimRecord } from "./api";
import { money, verdicts, words } from "./format";
import { SignOff } from "./SignOff";
import { StatusPill } from "./StatusPill";
import { Steps } from "./Steps";
import { useLive } from "./useLive";

function Details({ claim }: Readonly<{ claim: ClaimRecord }>) {
  return (
    <section className="card" aria-labelledby="details">
      <h2 id="details">The claim</h2>
      <dl className="facts">
        <dt>Type</dt>
        <dd>{words(claim.claim_type)}</dd>
        <dt>Incident</dt>
        <dd>
          {claim.incident_date}, {claim.incident_location}
        </dd>
        <dt>Submitted</dt>
        <dd>{claim.submitted_on}</dd>
        <dt>Policy</dt>
        <dd className="mono">{claim.policy_id}</dd>
      </dl>
      <h2 className="gap-top">In the customer's words</h2>
      <p>{claim.story}</p>
      <table className="items">
        <caption className="sr-only">Items claimed</caption>
        <tbody>
          {claim.items.map((item) => (
            <tr key={item.description}>
              <td>{item.description}</td>
              <td className="mono">{money(item.amount)}</td>
            </tr>
          ))}
          <tr>
            <td>
              <strong>Total claimed</strong>
            </td>
            <td className="mono">
              <strong>{money(claim.amount_claimed)}</strong>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  );
}

function Documents({ claim }: Readonly<{ claim: ClaimRecord }>) {
  return (
    <section className="card" aria-labelledby="documents">
      <h2 id="documents">Documents</h2>
      {claim.documents.map((document) => (
        <article className="document" key={document.name}>
          <strong>{document.name}</strong>
          <p>{document.content}</p>
        </article>
      ))}
    </section>
  );
}

function Outcome({
  claim,
  onChange,
}: Readonly<{
  claim: ClaimRecord;
  onChange: () => void;
}>) {
  const { decision, payment } = claim;
  return (
    <section className="card" aria-labelledby="decision">
      <h2 id="decision">Decision</h2>
      {decision ? (
        <>
          <p className="verdict">
            {verdicts[decision.decision]}
            {decision.decision === "approve" && (
              <span className="mono"> {money(decision.payout)}</span>
            )}
          </p>
          <p>{decision.reason}</p>
          <p className="mono muted">Section {decision.section}</p>
          {payment && (
            <p>
              Paid <span className="mono">{money(payment.amount)}</span>
              {decision.signed_off_by_name &&
                ` after sign-off by ${decision.signed_off_by_name}`}
            </p>
          )}
          {claim.status === "awaiting_signoff" && (
            <SignOff
              claimId={claim.claim_id}
              payout={decision.payout}
              signedOff={decision.signed_off_by !== null}
              onChange={onChange}
            />
          )}
        </>
      ) : (
        <p className="muted">No decision yet.</p>
      )}
    </section>
  );
}

/** One claim in full, kept up to date while the agent works on it. */
export function Claim({ id }: Readonly<{ id: string }>) {
  const load = useCallback(() => api.claim(id), [id]);
  const {
    data: claim,
    error,
    refresh,
  } = useLive(load, 1000, (current) =>
    ["waiting", "in_progress"].includes(current.status),
  );

  if (error)
    return (
      <p className="error">
        Couldn't load {id}: {error}
      </p>
    );
  if (!claim) return <p>Loading {id}</p>;

  return (
    <>
      <p>
        <a href="#/">Back to the queue</a>
      </p>
      <h1 className="mono">{claim.claim_id}</h1>
      <p className="lede">
        {claim.summary} <StatusPill status={claim.status} />
      </p>
      <div className="claim-grid">
        <div className="stack">
          <Details claim={claim} />
          <Documents claim={claim} />
        </div>
        <div className="stack">
          <Outcome claim={claim} onChange={refresh} />
          <Steps steps={claim.steps} working={claim.status === "in_progress"} />
        </div>
      </div>
    </>
  );
}
