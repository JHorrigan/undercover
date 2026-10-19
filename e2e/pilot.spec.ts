import { expect, test } from "@playwright/test";

test("the queue lists every claim with its status", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("25 claims")).toBeVisible();
  await expect(page.locator("tbody tr")).toHaveCount(25);
  await expect(page.getByRole("link", { name: "CLM-1001" })).toBeVisible();
});

test("a claim page shows the claim in full", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "CLM-1002" }).click();
  await expect(
    page.getByRole("heading", { name: "Suitcase lost on a connecting flight" }),
  ).toBeVisible();
  await expect(page.getByText("What the customer told us")).toBeVisible();
  await expect(page.getByText("Total claimed")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Run the agent" }),
  ).toBeVisible();
});

test("a payout over $1,000 is held until a handler signs off", async ({
  page,
  request,
}) => {
  const claim = "/api/claims/CLM-1008";
  const decision = await request.post(`${claim}/decision`, {
    data: {
      decision: "approve",
      payout: 1500,
      reason: "A covered cancellation.",
      policy_section: "2. Trip Cancellation and Interruption",
    },
  });
  expect(decision.ok()).toBe(true);
  const payment = await request.post(`${claim}/payment`, {
    data: { amount: 1500 },
  });
  expect(payment.status()).toBe(403);

  await page.goto("/#/claims/CLM-1008");
  await expect(page.getByText("Waiting for sign-off").first()).toBeVisible();
  await expect(page.getByText(/^Paid/)).toHaveCount(0);
  await page.getByLabel("Handler").selectOption("HND-02");
  await page
    .getByRole("button", { name: "Sign off and pay $1,500.00" })
    .click();
  await expect(
    page.getByText(/after sign-off by Marcus Oyelaran/),
  ).toBeVisible();
  await expect(page.getByText("Decided")).toBeVisible();
});

test("the agent's instructions are read only", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Instructions" }).click();
  await expect(page.getByText("# Working a claim")).toBeVisible();
  await expect(page.getByRole("textbox")).toHaveCount(0);
  await expect(page.getByRole("button")).toHaveCount(0);
});
