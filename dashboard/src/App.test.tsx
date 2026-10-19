import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import type { ClaimSummary } from "./api";
import { getJson } from "./api";
import { App } from "./App";
import { humanize, money } from "./format";
import { parseRoute } from "./hooks";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.location.hash = "";
});

const summary = (id: string, status: ClaimSummary["status"]): ClaimSummary => ({
  claim_id: id,
  customer_id: "CUS-3001",
  customer_name: "Maya Patel",
  claim_type: "trip_delay",
  summary: "Flight home canceled",
  amount_claimed: 420,
  submitted_on: "2026-06-24",
  status,
  failures: 0,
});

function stubFetch(body: unknown, status = 200) {
  vi.stubGlobal(
    "fetch",
    vi.fn((path: string) =>
      Promise.resolve(
        path === "/api/runs/latest"
          ? new Response("null")
          : new Response(JSON.stringify(body), { status }),
      ),
    ),
  );
}

it("shows the queue with each claim's status", async () => {
  stubFetch([
    summary("CLM-1001", "waiting"),
    summary("CLM-1002", "awaiting_signoff"),
    summary("CLM-1003", "decided"),
    summary("CLM-1004", "needs_handler"),
  ]);
  render(<App />);
  const table = await screen.findByRole("table");
  expect(within(table).getByText("CLM-1001")).toBeDefined();
  expect(within(table).getByText("Waiting for sign-off")).toBeDefined();
  expect(within(table).getByText("Needs a handler")).toBeDefined();
  expect(within(table).getAllByText("$420.00")).toHaveLength(4);
  const legend = screen.getByRole("list", { name: "Claims by status" });
  expect(within(legend).getByText("Decided").previousSibling?.textContent).toBe(
    "1",
  );
});

it("says when the queue can't load", async () => {
  stubFetch({ detail: "Database is down" }, 500);
  render(<App />);
  expect(await screen.findByText(/Database is down/)).toBeDefined();
});

it("parses routes", () => {
  expect(parseRoute("")).toEqual({ page: "queue" });
  expect(parseRoute("#/claims/CLM-1001")).toEqual({
    page: "claim",
    id: "CLM-1001",
  });
  expect(parseRoute("#/instructions")).toEqual({ page: "instructions" });
});

it("formats money and codes", () => {
  expect(money(1250)).toBe("$1,250.00");
  expect(humanize("emergency_medical")).toBe("Emergency medical");
});

it("reports a status code when there is no detail", async () => {
  stubFetch({}, 502);
  await expect(getJson("/api/claims")).rejects.toThrow("failed with 502");
});
