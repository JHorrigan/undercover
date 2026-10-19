export type Status =
  "waiting" | "in_progress" | "awaiting_signoff" | "decided" | "needs_handler";

export interface ClaimSummary {
  claim_id: string;
  customer_id: string;
  customer_name: string;
  claim_type: string;
  summary: string;
  amount_claimed: number;
  submitted_on: string;
  status: Status;
  failures: number;
}

export interface Item {
  description: string;
  category: string;
  amount: number;
}

export interface ClaimDocument {
  name: string;
  type: string;
  content: string;
}

export interface Decision {
  decision: "approve" | "decline" | "refer";
  payout: number;
  reason: string;
  policy_section: string;
  decided_at: string;
}

export interface Claim {
  claim_id: string;
  policy_id: string;
  customer_id: string;
  claim_type: string;
  summary: string;
  story: string;
  submitted_on: string;
  incident_date: string;
  incident_location: string;
  amount_claimed: number;
  items: Item[];
  documents: ClaimDocument[];
  status: Status;
  decision: Decision | null;
  payment: { amount: number; paid_at: string } | null;
  sign_off: {
    handler_id: string;
    handler_name: string;
    signed_at: string;
  } | null;
  failures: number;
}

export interface Policy {
  policy_id: string;
  plan: string;
  add_ons: string[];
  purchased_on: string;
  trip: {
    destination: string;
    departs_on: string;
    returns_on: string;
    trip_cost: number;
  };
  travelers: string[];
}

export interface Customer {
  customer_id: string;
  name: string;
  customer_since: string;
  previous_claims: {
    claim_id: string;
    filed_on: string;
    claim_type: string;
    summary: string;
    outcome: string;
    amount_paid: number;
  }[];
}

export interface Handler {
  handler_id: string;
  name: string;
  role: string;
  can_approve_over_limit: boolean;
}

export interface Step {
  id: number;
  at: string;
  kind: "tool" | "result" | "reply" | "read" | "error";
  text: string;
}

export type TodoStatus = "to_do" | "in_progress" | "done" | "for_handler";

export interface Todo {
  text: string;
  status: TodoStatus;
}

export interface Run {
  run_id: string;
  cap: number;
  started_at: string;
  finished_at: string | null;
  summary: string | null;
  todos: Todo[];
}

export type AgentName = "queue" | "claim";

export function errorMessage(reason: unknown): string {
  return reason instanceof Error ? reason.message : String(reason);
}

async function read(response: Response): Promise<Response> {
  if (response.ok) return response;
  const body = (await response.json()) as { detail?: string };
  throw new Error(
    body.detail ?? `The request failed with ${String(response.status)}`,
  );
}

export async function getJson<T>(path: string): Promise<T> {
  const response = await read(await fetch(path));
  return (await response.json()) as T;
}

export async function getText(path: string): Promise<string> {
  const response = await read(await fetch(path));
  return response.text();
}

export async function postJson<T>(path: string, body: object): Promise<T> {
  const response = await read(
    await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
  return (await response.json()) as T;
}

export const api = {
  claims: () => getJson<ClaimSummary[]>("/api/claims"),
  claim: (id: string) => getJson<Claim>(`/api/claims/${id}`),
  policy: (id: string) => getJson<Policy>(`/api/policies/${id}`),
  customer: (id: string) => getJson<Customer>(`/api/customers/${id}`),
  handlers: () => getJson<Handler[]>("/api/handlers"),
  steps: (id: string) => getJson<Step[]>(`/api/claims/${id}/steps`),
  instructions: (agent: AgentName) => getText(`/api/instructions/${agent}`),
  latestRun: () => getJson<Run | null>("/api/runs/latest"),
  startRun: (cap: number) =>
    postJson<{ status: string }>("/api/runs/start", { cap }),
  runAgent: (id: string) =>
    postJson<{ status: string }>(`/api/claims/${id}/run`, {}),
  signOff: (id: string, handlerId: string) =>
    postJson<Claim>(`/api/claims/${id}/sign-off`, { handler_id: handlerId }),
};
