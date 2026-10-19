import { api } from "./api";
import { humanize, money } from "./format";
import { useData } from "./hooks";
import { RunPanel } from "./RunPanel";
import { StatusBadge, StatusBar } from "./Status";

const REFRESH_MS = 3000;

export function Queue() {
  const { data: claims, error } = useData(api.claims, REFRESH_MS);
  return (
    <>
      <div className="page-head">
        <h1>Claims queue</h1>
        {claims && <span className="muted">{claims.length} claims</span>}
      </div>
      <RunPanel />
      {error && <p className="error">Couldn't load the queue: {error}</p>}
      {claims && (
        <>
          <StatusBar statuses={claims.map((c) => c.status)} />
          <section className="panel table-scroll">
            <table className="queue">
              <thead>
                <tr>
                  <th>Claim</th>
                  <th>Customer</th>
                  <th>What happened</th>
                  <th>Submitted</th>
                  <th className="amount">Claimed</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr key={claim.claim_id}>
                    <td>
                      <a className="mono" href={`#/claims/${claim.claim_id}`}>
                        {claim.claim_id}
                      </a>
                    </td>
                    <td>{claim.customer_name}</td>
                    <td>
                      {claim.summary}
                      <div className="muted">{humanize(claim.claim_type)}</div>
                    </td>
                    <td className="mono">{claim.submitted_on}</td>
                    <td className="mono amount">
                      {money(claim.amount_claimed)}
                    </td>
                    <td>
                      <StatusBadge status={claim.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </>
  );
}
