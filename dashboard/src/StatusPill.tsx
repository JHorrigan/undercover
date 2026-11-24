import type { Status } from "./api";
import { statusLabels } from "./format";

/** A claim's status as a label pill, with its name in text. */
export function StatusPill({ status }: Readonly<{ status: Status }>) {
  return <span className={`pill tone-${status}`}>{statusLabels[status]}</span>;
}
