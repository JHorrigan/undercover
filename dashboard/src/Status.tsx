import type { Status } from "./api";
import { STATUS_LABEL, STATUSES } from "./format";

export function StatusBadge({ status }: Readonly<{ status: Status }>) {
  return (
    <span className={`badge status-${status}`}>{STATUS_LABEL[status]}</span>
  );
}

/** A bar split by how many claims are in each status, with a legend. */
export function StatusBar({ statuses }: Readonly<{ statuses: Status[] }>) {
  const counts = STATUSES.map((status) => ({
    status,
    count: statuses.filter((s) => s === status).length,
  }));
  return (
    <>
      <div className="status-bar" aria-hidden="true">
        {counts.map(({ status, count }) => (
          <span
            key={status}
            className={`status-${status}`}
            style={{ flexGrow: count }}
          />
        ))}
      </div>
      <ul className="status-legend" aria-label="Claims by status">
        {counts.map(({ status, count }) => (
          <li key={status}>
            <span className={`dot status-${status}`} />
            <span className="count">{count}</span>
            <span>{STATUS_LABEL[status]}</span>
          </li>
        ))}
      </ul>
    </>
  );
}
