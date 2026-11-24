import { vi } from "vitest";
import type { Claim, Decision, QueueClaim } from "./api";

export const queueClaim: QueueClaim = {
  claim_id: "CLM-1001",
  claim_type: "trip_delay",
  summary: "Flight home canceled by the airline",
  submitted_on: "2026-06-24",
  amount_claimed: 1420,
  status: "awaiting_signoff",
};

export const decision: Decision = {
  decision: "approve",
  payout: 1420,
  reason: "The delay is covered.",
  section: "3. Trip Delay",
  signed_off_by: null,
  signed_off_by_name: null,
};

export const claim: Claim = {
  ...queueClaim,
  policy_id: "POL-2001",
  incident_date: "2026-06-18",
  incident_location: "Rome, Italy",
  story: "My flight home from Rome was canceled.",
  items: [
    { description: "Airport hotel", category: "accommodation", amount: 1420 },
  ],
  documents: [
    {
      name: "Hotel receipt",
      type: "receipt",
      content: "One night, $1,420.00.",
    },
  ],
  decision,
  payment: null,
  steps: [
    {
      recorded_at: "2026-11-24T10:00:00+00:00",
      text: "get_policy",
      cost: 0.0021,
    },
  ],
};

/** Stub fetch with a reply for each path, and record what was sent. */
export function stubApi(replies: Record<string, unknown>) {
  const fetchMock = vi.fn((path: string) => {
    if (!(path in replies))
      return Promise.resolve(new Response("{}", { status: 404 }));
    const reply = replies[path];
    if (reply instanceof Response) return Promise.resolve(reply);
    return Promise.resolve(new Response(JSON.stringify(reply)));
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}
