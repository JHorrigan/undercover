import type { Status } from "./api";
import { statusLabels } from "./format";

export function StatusPill({ status }: Readonly<{ status: Status }>) {
  return <span className={`pill tone-${status}`}>{statusLabels[status]}</span>;
}
