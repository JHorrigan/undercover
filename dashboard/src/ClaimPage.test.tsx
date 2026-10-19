import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import type { Claim, Step } from "./api";
import { App } from "./App";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.location.hash = "";
});

const claim = (changes: Partial<Claim>): Claim => ({
  claim_id: "CLM-1003",
  policy_id: "POL-2003",
  customer_id: "CUS-3003",
  claim_type: "emergency_medical",
  summary: "Fractured wrist",
  story: "I slipped on wet cobblestones.",
  submitted_on: "2026-07-06",
  incident_date: "2026-06-27",
  incident_location: "Lisbon, Portugal",
  amount_claimed: 3800,
  items: [{ description: "Hospital bill", category: "medical", amount: 3800 }],
  documents: [
    { name: "Medical report", type: "report", content: "A fracture." },
  ],
  status: "waiting",
  decision: null,
  payment: null,
  sign_off: null,
  failures: 0,
  ...changes,
});

const approved = {
  decision: "approve" as const,
  payout: 3750,
  reason: "A sudden injury on a covered trip.",
  policy_section: "7. Emergency Medical",
  decided_at: "2026-10-18T17:20:07+00:00",
};

const policy = {
  policy_id: "POL-2003",
  plan: "premium",
  add_ons: [],
  purchased_on: "2026-05-04",
  trip: {
    destination: "Lisbon",
    departs_on: "2026-06-20",
    returns_on: "2026-07-01",
    trip_cost: 2900,
  },
  travelers: ["Aiko Tanaka"],
};

const customer = {
  customer_id: "CUS-3003",
  name: "Aiko Tanaka",
  customer_since: "2024-01-01",
  previous_claims: [],
};

const handlers = [
  {
    handler_id: "HND-01",
    name: "Dana Whitfield",
    role: "Senior Claims Handler",
    can_approve_over_limit: true,
  },
];

function serve(current: Claim, steps: Step[] = []) {
  const routes: Record<string, unknown> = {
    "/api/claims/CLM-1003": current,
    "/api/claims/CLM-1003/steps": steps,
    "/api/policies/POL-2003": policy,
    "/api/customers/CUS-3003": customer,
    "/api/handlers": handlers,
    "/api/claims/CLM-1003/run": { status: "started" },
    "/api/claims/CLM-1003/sign-off": current,
  };
  const fetchMock = vi.fn((path: string) =>
    Promise.resolve(new Response(JSON.stringify(routes[path]))),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function openClaim() {
  window.location.hash = "#/claims/CLM-1003";
  render(<App />);
}

it("shows the claim, its policy and a way to run the agent", async () => {
  const fetchMock = serve(claim({}));
  openClaim();
  expect(
    await screen.findByText("I slipped on wet cobblestones."),
  ).toBeDefined();
  expect(screen.getByText("A fracture.")).toBeDefined();
  expect(await screen.findByText("Premium")).toBeDefined();
  expect(screen.getByText("None.")).toBeDefined();
  fireEvent.click(screen.getByRole("button", { name: "Run the agent" }));
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/claims/CLM-1003/run",
      expect.objectContaining({ method: "POST" }),
    );
  });
});

it("shows the agent's steps while it works", async () => {
  serve(claim({ status: "in_progress" }), [
    { id: 1, at: "", kind: "tool", text: "get_claim {'claim_id': 'CLM-1003'}" },
    { id: 2, at: "", kind: "reply", text: "Approved." },
  ]);
  openClaim();
  expect(
    await screen.findByText("The agent is working on this claim."),
  ).toBeDefined();
  expect(
    await screen.findByText("get_claim {'claim_id': 'CLM-1003'}"),
  ).toBeDefined();
  expect(screen.getByText("Said")).toBeDefined();
});

it("lists the sections the agent read and what went wrong", async () => {
  serve(claim({ status: "waiting", failures: 1 }), [
    { id: 1, at: "", kind: "read", text: "Claims manual: 9. Repeat claims" },
    {
      id: 2,
      at: "",
      kind: "error",
      text: "RuntimeError: Provider returned 502",
    },
  ]);
  openClaim();
  const panel = await screen.findByRole("heading", {
    name: "What the agent read",
  });
  expect(panel.nextElementSibling?.textContent).toBe(
    "Claims manual: 9. Repeat claims",
  );
  expect(screen.getByText("Read")).toBeDefined();
  expect(screen.getByText("Went wrong")).toBeDefined();
});

it("has no reading panel before the agent reads anything", async () => {
  serve(claim({}));
  openClaim();
  await screen.findByText("I slipped on wet cobblestones.");
  expect(screen.queryByText("What the agent read")).toBeNull();
});

it("holds a payout over the limit until a handler signs off", async () => {
  const fetchMock = serve(
    claim({ status: "awaiting_signoff", decision: approved }),
  );
  openClaim();
  expect(
    await screen.findByText("A sudden injury on a covered trip."),
  ).toBeDefined();
  const button = screen.getByRole("button", {
    name: "Sign off and pay $3,750.00",
  });
  expect(button).toHaveProperty("disabled", true);
  await screen.findByRole("option", { name: "Dana Whitfield" });
  fireEvent.change(screen.getByLabelText("Handler"), {
    target: { value: "HND-01" },
  });
  fireEvent.click(button);
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/claims/CLM-1003/sign-off",
      expect.objectContaining({
        body: JSON.stringify({ handler_id: "HND-01" }),
      }),
    );
  });
});

it("shows the payment after sign-off", async () => {
  serve(
    claim({
      status: "decided",
      decision: approved,
      payment: { amount: 3750, paid_at: "2026-10-18T17:20:27+00:00" },
      sign_off: {
        handler_id: "HND-01",
        handler_name: "Dana Whitfield",
        signed_at: "2026-10-18T17:20:27+00:00",
      },
    }),
  );
  openClaim();
  expect(
    await screen.findByText(/after sign-off by Dana Whitfield/),
  ).toBeDefined();
});

it("shows both agents' instructions read only", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn((path: string) =>
      Promise.resolve(new Response(`# Instructions from ${path}`)),
    ),
  );
  window.location.hash = "#/instructions";
  render(<App />);
  expect(screen.getByRole("heading", { name: "Queue agent" })).toBeDefined();
  expect(screen.getByRole("heading", { name: "Claim agent" })).toBeDefined();
  expect(
    await screen.findByText("# Instructions from /api/instructions/queue"),
  ).toBeDefined();
  expect(
    await screen.findByText("# Instructions from /api/instructions/claim"),
  ).toBeDefined();
  expect(screen.queryByRole("textbox")).toBeNull();
  expect(screen.queryByRole("button")).toBeNull();
});
