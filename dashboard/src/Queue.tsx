import { api, type QueueClaim, type Status } from "./api";
import { money, statusLabels, words } from "./format";
import { StatusPill } from "./StatusPill";
import { useLive } from "./useLive";

const order: Status[] = [
  "waiting",
  "in_progress",
  "awaiting_signoff",
  "decided",
];

function Counts({ claims }: Readonly<{ claims: QueueClaim[] }>) {
  return (
    <ul className="counts" aria-label="Claims by status">
      {order.map((status) => (
        <li key={status} className={`tone-${status}`}>
          <strong className="mono">
            {claims.filter((claim) => claim.status === status).length}
          </strong>
          <span>{statusLabels[status]}</span>
        </li>
      ))}
    </ul>
  );
}

/** The claims queue, oldest first, with counts by status. */
export function Queue() {
  const { data, error } = useLive(api.queue, 2000, (claims) =>
    claims.some((claim) => claim.status !== "decided"),
  );

  return (
    <>
      <h1>Claims queue</h1>
      <p className="lede">Oldest first. The agent takes claims from the top.</p>
      {error && <p className="error">Couldn't load the queue: {error}</p>}
      {data && (
        <>
          <Counts claims={data} />
          <section className="card" aria-label="Claims">
            <table className="queue">
              <thead>
                <tr>
                  <th scope="col">Claim</th>
                  <th scope="col" className="hide-small">
                    Type
                  </th>
                  <th scope="col" className="hide-small">
                    Summary
                  </th>
                  <th scope="col" className="money">
                    Claimed
                  </th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.map((claim) => (
                  <tr key={claim.claim_id}>
                    <td className="mono">
                      <a href={`#/claims/${claim.claim_id}`}>
                        {claim.claim_id}
                      </a>
                    </td>
                    <td className="hide-small">{words(claim.claim_type)}</td>
                    <td className="summary hide-small">{claim.summary}</td>
                    <td className="money mono">
                      {money(claim.amount_claimed)}
                    </td>
                    <td>
                      <StatusPill status={claim.status} />
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
