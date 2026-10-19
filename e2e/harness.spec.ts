import { expect, test } from "@playwright/test";

test("the queue page shows the agent's run and its to-do list", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Agent run" })).toBeVisible();
  await expect(page.getByLabel("Claims to work")).toHaveValue("5");

  const run = await request.post("/api/runs", { data: { cap: 2 } });
  const { run_id } = (await run.json()) as { run_id: string };
  await request.put(`/api/runs/${run_id}/todos`, {
    data: {
      todos: [
        { text: "Work CLM-1001", status: "done" },
        { text: "Work CLM-1002", status: "in_progress" },
      ],
    },
  });

  await expect(
    page.getByRole("heading", { name: "The agent is working the queue" }),
  ).toBeVisible();
  const list = page.getByRole("list", { name: "The agent's to-do list" });
  await expect(list.getByRole("listitem")).toHaveText([
    "DoneWork CLM-1001",
    "In progressWork CLM-1002",
  ]);
  await expect(page.getByText(/1 of 2 done/)).toBeVisible();
});

test("a claim page lists the sections the agent read", async ({
  page,
  request,
}) => {
  await request.post("/api/claims/CLM-1005/steps", {
    data: { kind: "read", text: "Claims manual: 9. Repeat claims" },
  });
  await page.goto("/#/claims/CLM-1005");
  const reads = page
    .getByRole("heading", { name: "What the agent read" })
    .locator("xpath=..");
  await expect(
    reads.getByText("Claims manual: 9. Repeat claims"),
  ).toBeVisible();
});

test("the instructions page shows both agents", async ({ page }) => {
  await page.goto("/#/instructions");
  await expect(
    page.getByRole("heading", { name: "Queue agent" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Claim agent" }),
  ).toBeVisible();
  await expect(page.getByText("# Running the queue")).toBeVisible();
  await expect(page.getByText("# Working a claim")).toBeVisible();
});
