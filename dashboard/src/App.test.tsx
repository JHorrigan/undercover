import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { App } from "./App";
import { claim, decision, queueClaim, stubApi } from "./testing";

beforeEach(() => {
  window.location.hash = "";
  localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("shows the queue with each claim's status and amount", async () => {
  stubApi({ "/api/claims": [queueClaim] });
  render(<App />);
  expect(await screen.findByRole("link", { name: "CLM-1001" })).toBeDefined();
  expect(screen.getByText("$1,420.00")).toBeDefined();
  expect(screen.getByText("Trip delay")).toBeDefined();
  expect(screen.getAllByText("Waiting for sign-off").length).toBeGreaterThan(0);
});

it("says when the queue can't be loaded", async () => {
  stubApi({});
  render(<App />);
  expect(await screen.findByText(/Couldn't load the queue/)).toBeDefined();
});

it("shows a claim in full with the agent's decision and steps", async () => {
  stubApi({ "/api/claims/CLM-1001": claim, "/api/handlers": [] });
  window.location.hash = "#/claims/CLM-1001";
  render(<App />);
  expect(
    await screen.findByText("My flight home from Rome was canceled."),
  ).toBeDefined();
  expect(screen.getByText("One night, $1,420.00.")).toBeDefined();
  expect(screen.getByText("Approved")).toBeDefined();
  expect(screen.getByText("The delay is covered.")).toBeDefined();
  expect(screen.getByText("Section 3. Trip Delay")).toBeDefined();
  expect(screen.getByText("get_policy")).toBeDefined();
  expect(screen.getByText("Model cost $0.0021")).toBeDefined();
});

it("says when a claim can't be loaded", async () => {
  stubApi({});
  window.location.hash = "#/claims/CLM-1001";
  render(<App />);
  expect(
    await screen.findByText(
      "Couldn't load CLM-1001: /api/claims/CLM-1001 returned 404",
    ),
  ).toBeDefined();
});

it("pays a claim already signed off without signing off again", async () => {
  const signedOff = {
    ...claim,
    decision: {
      ...decision,
      signed_off_by: "HND-01",
      signed_off_by_name: "Dana Whitfield",
    },
  };
  const fetchMock = stubApi({
    "/api/claims/CLM-1001": signedOff,
    "/api/handlers": [],
    "/api/claims/CLM-1001/payment": null,
  });
  window.location.hash = "#/claims/CLM-1001";
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "Pay" }));
  await vi.waitFor(() => {
    const sent = fetchMock.mock.calls.map((call) => call[0]);
    expect(sent).toContain("/api/claims/CLM-1001/payment");
    expect(sent).not.toContain("/api/claims/CLM-1001/sign-off");
  });
});

it("signs off and pays a claim over the limit", async () => {
  const fetchMock = stubApi({
    "/api/claims/CLM-1001": claim,
    "/api/handlers": [
      { handler_id: "HND-01", name: "Dana Whitfield", can_sign_off: true },
      { handler_id: "HND-09", name: "Sam Trainee", can_sign_off: false },
    ],
    "/api/claims/CLM-1001/sign-off": null,
    "/api/claims/CLM-1001/payment": null,
  });
  window.location.hash = "#/claims/CLM-1001";
  render(<App />);
  expect(
    await screen.findByRole("option", { name: "Dana Whitfield" }),
  ).toBeDefined();
  expect(screen.queryByRole("option", { name: "Sam Trainee" })).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Sign off and pay" }));
  await vi.waitFor(() => {
    const sent = fetchMock.mock.calls.map((call) => call[0]);
    expect(sent).toContain("/api/claims/CLM-1001/payment");
  });
  expect(fetchMock).toHaveBeenCalledWith(
    "/api/claims/CLM-1001/sign-off",
    expect.objectContaining({ body: JSON.stringify({ handler_id: "HND-01" }) }),
  );
});

it("shows why a sign-off was refused", async () => {
  stubApi({
    "/api/claims/CLM-1001": claim,
    "/api/handlers": [
      { handler_id: "HND-01", name: "Dana Whitfield", can_sign_off: true },
    ],
    "/api/claims/CLM-1001/sign-off": new Response(
      JSON.stringify({ detail: "CLM-1001 is already signed off" }),
      { status: 409 },
    ),
  });
  window.location.hash = "#/claims/CLM-1001";
  render(<App />);
  await screen.findByRole("option", { name: "Dana Whitfield" });
  fireEvent.click(screen.getByRole("button", { name: "Sign off and pay" }));
  expect((await screen.findByRole("alert")).textContent).toBe(
    "CLM-1001 is already signed off",
  );
});

it("shows the agent's instructions, read only", async () => {
  stubApi({ "/api/instructions": { text: "# The UnderCover Agent" } });
  window.location.hash = "#/instructions";
  render(<App />);
  expect(await screen.findByText("# The UnderCover Agent")).toBeDefined();
});

it("switches between dark and light mode and remembers it", async () => {
  stubApi({ "/api/claims": [] });
  render(<App />);
  expect(document.documentElement.dataset.theme).toBe("dark");
  fireEvent.click(await screen.findByRole("button", { name: "Light mode" }));
  expect(document.documentElement.dataset.theme).toBe("light");
  expect(localStorage.getItem("theme")).toBe("light");
});
