import type { Status } from "./api";

export const STATUSES: Status[] = [
  "waiting",
  "in_progress",
  "awaiting_signoff",
  "decided",
];

export const STATUS_LABEL: Record<Status, string> = {
  waiting: "Waiting",
  in_progress: "In progress",
  awaiting_signoff: "Waiting for sign-off",
  decided: "Decided",
};

const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function money(amount: number): string {
  return usd.format(amount);
}

export function humanize(code: string): string {
  const words = code.replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}
