import type { Status, TodoStatus } from "./api";

export const STATUSES: Status[] = [
  "waiting",
  "in_progress",
  "awaiting_signoff",
  "decided",
  "needs_handler",
];

export const STATUS_LABEL: Record<Status, string> = {
  waiting: "Waiting",
  in_progress: "In progress",
  awaiting_signoff: "Waiting for sign-off",
  decided: "Decided",
  needs_handler: "Needs a handler",
};

export const TODO_STATUSES: TodoStatus[] = [
  "done",
  "in_progress",
  "to_do",
  "for_handler",
];

export const TODO_LABEL: Record<TodoStatus, string> = {
  to_do: "To do",
  in_progress: "In progress",
  done: "Done",
  for_handler: "For a handler",
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
