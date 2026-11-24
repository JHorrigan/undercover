export type Status = "waiting" | "in_progress" | "awaiting_signoff" | "decided";

export interface QueueClaim {
  claim_id: string;
  claim_type: string;
  summary: string;
  submitted_on: string;
  amount_claimed: number;
  status: Status;
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
  section: string;
  signed_off_by: string | null;
  signed_off_by_name: string | null;
}

export interface Step {
  recorded_at: string;
  text: string;
  cost: number;
}

export interface Claim extends QueueClaim {
  policy_id: string;
  incident_date: string;
  incident_location: string;
  story: string;
  items: Item[];
  documents: ClaimDocument[];
  decision: Decision | null;
  payment: { amount: number; paid_at: string } | null;
  steps: Step[];
}

export interface Handler {
  handler_id: string;
  name: string;
  can_sign_off: boolean;
}

async function read<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok)
    throw new Error(`${path} returned ${String(response.status)}`);
  return (await response.json()) as T;
}

async function send(path: string, body: object): Promise<void> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const { detail } = (await response.json()) as { detail: unknown };
    throw new Error(
      typeof detail === "string" ? detail : "The request was rejected",
    );
  }
}

export const api = {
  queue: () => read<QueueClaim[]>("/api/claims"),
  claim: (id: string) => read<Claim>(`/api/claims/${id}`),
  handlers: () => read<Handler[]>("/api/handlers"),
  instructions: () => read<{ text: string }>("/api/instructions"),
  signOff: (id: string, handlerId: string) =>
    send(`/api/claims/${id}/sign-off`, { handler_id: handlerId }),
  pay: (id: string, amount: number) =>
    send(`/api/claims/${id}/payment`, { amount }),
};
