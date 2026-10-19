import { useCallback } from "react";
import type { Claim } from "./api";
import { api } from "./api";
import { humanize, money } from "./format";
import { useData } from "./hooks";

/** The claim as the customer made it: story, items, documents, policy and history. */
export function Evidence({ claim }: Readonly<{ claim: Claim }>) {
  return (
    <div className="stack">
      <section className="panel">
        <h2>What the customer told us</h2>
        <p className="story">{claim.story}</p>
        <p className="muted">
          {claim.incident_location}, on {claim.incident_date}. Submitted{" "}
          {claim.submitted_on}.
        </p>
      </section>
      <Items claim={claim} />
      <section className="panel">
        <h2>Documents</h2>
        {claim.documents.map((doc) => (
          <div className="document" key={doc.name}>
            <h3>{doc.name}</h3>
            <p>{doc.content}</p>
          </div>
        ))}
      </section>
      <PolicyAndHistory claim={claim} />
    </div>
  );
}

function Items({ claim }: Readonly<{ claim: Claim }>) {
  return (
    <section className="panel">
      <h2>Items claimed</h2>
      <table className="items">
        <tbody>
          {claim.items.map((item) => (
            <tr key={item.description}>
              <td>
                {item.description}
                <div className="muted">{humanize(item.category)}</div>
              </td>
              <td className="mono amount">{money(item.amount)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th scope="row">Total claimed</th>
            <td className="mono amount">{money(claim.amount_claimed)}</td>
          </tr>
        </tfoot>
      </table>
    </section>
  );
}

function PolicyAndHistory({ claim }: Readonly<{ claim: Claim }>) {
  const loadPolicy = useCallback(() => api.policy(claim.policy_id), [claim]);
  const loadCustomer = useCallback(
    () => api.customer(claim.customer_id),
    [claim],
  );
  const { data: policy } = useData(loadPolicy, 0);
  const { data: customer } = useData(loadCustomer, 0);
  return (
    <section className="panel">
      <h2>Policy and history</h2>
      {policy && (
        <dl className="facts">
          <dt>Plan</dt>
          <dd>{humanize(policy.plan)}</dd>
          <dt>Add-ons</dt>
          <dd>{policy.add_ons.map(humanize).join(", ") || "None"}</dd>
          <dt>Bought</dt>
          <dd className="mono">{policy.purchased_on}</dd>
          <dt>Trip</dt>
          <dd>
            {policy.trip.destination},{" "}
            <span className="mono">
              {policy.trip.departs_on} to {policy.trip.returns_on}
            </span>
          </dd>
          <dt>Trip cost</dt>
          <dd className="mono">{money(policy.trip.trip_cost)}</dd>
          <dt>Travelers</dt>
          <dd>{policy.travelers.join(", ")}</dd>
        </dl>
      )}
      {customer && (
        <>
          <h3>Earlier claims from {customer.name}</h3>
          {customer.previous_claims.length === 0 && (
            <p className="muted">None.</p>
          )}
          <ul className="history">
            {customer.previous_claims.map((c) => (
              <li key={c.claim_id}>
                <span className="mono">{c.filed_on}</span> {c.summary}.{" "}
                {humanize(c.outcome)}, {money(c.amount_paid)} paid.
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
