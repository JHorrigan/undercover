import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import type { Run } from "./api";
import { RunPanel } from "./RunPanel";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const run = (changes: Partial<Run>): Run => ({
  run_id: "RUN-1a2b3c4d",
  cap: 5,
  started_at: "2026-10-19T09:00:00+00:00",
  finished_at: null,
  summary: null,
  todos: [],
  ...changes,
});

function serve(latest: Run | null, start: Response = new Response("{}")) {
  const fetchMock = vi.fn((path: string) =>
    Promise.resolve(
      path === "/api/runs/start" ? start : new Response(JSON.stringify(latest)),
    ),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

it("starts a run capped at the number of claims chosen", async () => {
  const fetchMock = serve(null);
  render(<RunPanel />);
  expect(screen.getByRole("heading", { name: "Agent run" })).toBeDefined();
  fireEvent.change(screen.getByLabelText("Claims to work"), {
    target: { value: "3" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Run the queue" }));
  await waitFor(() => {
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/runs/start",
      expect.objectContaining({ body: JSON.stringify({ cap: 3 }) }),
    );
  });
});

it("says why a run could not start", async () => {
  serve(
    null,
    new Response(JSON.stringify({ detail: "A run is already going" }), {
      status: 409,
    }),
  );
  render(<RunPanel />);
  fireEvent.click(screen.getByRole("button", { name: "Run the queue" }));
  expect(await screen.findByText("A run is already going")).toBeDefined();
});

it("shows the to-do list of a run in progress", async () => {
  serve(
    run({
      todos: [
        { text: "Work CLM-1001", status: "done" },
        { text: "Work CLM-1002", status: "in_progress" },
        { text: "Work CLM-1003", status: "to_do" },
        { text: "Work CLM-1004", status: "for_handler" },
      ],
    }),
  );
  render(<RunPanel />);
  expect(
    await screen.findByRole("heading", {
      name: "The agent is working the queue",
    }),
  ).toBeDefined();
  expect(screen.getByText(/capped at 5 claims, 1 of 4 done/)).toBeDefined();
  const list = screen.getByRole("list", { name: "The agent's to-do list" });
  const items = within(list).getAllByRole("listitem");
  expect(items.map((item) => item.textContent)).toEqual([
    "DoneWork CLM-1001",
    "In progressWork CLM-1002",
    "To doWork CLM-1003",
    "For a handlerWork CLM-1004",
  ]);
  expect(screen.queryByRole("button", { name: "Run the queue" })).toBeNull();
});

it("shows the summary of a finished run", async () => {
  serve(
    run({
      cap: 1,
      finished_at: "2026-10-19T09:05:00+00:00",
      summary: "One claim decided and paid.",
    }),
  );
  render(<RunPanel />);
  expect(await screen.findByText("One claim decided and paid.")).toBeDefined();
  expect(screen.getByText(/capped at 1 claim, finished/)).toBeDefined();
  expect(
    screen.getByText("The agent's to-do list appears here."),
  ).toBeDefined();
  expect(screen.getByRole("button", { name: "Run the queue" })).toBeDefined();
});
