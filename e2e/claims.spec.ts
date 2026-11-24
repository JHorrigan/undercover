import AxeBuilder from "@axe-core/playwright";
import {
  expect,
  test,
  type APIRequestContext,
  type Page,
} from "@playwright/test";
import { backendUrl } from "../playwright.config";

/** Take the oldest waiting claim and approve it for $1,500, over the limit. */
async function claimWaitingForSignOff(request: APIRequestContext) {
  const taken = await request.post(`${backendUrl}/api/queue/next`);
  const { claim_id } = (await taken.json()) as { claim_id: string };
  await request.post(`${backendUrl}/api/claims/${claim_id}/decision`, {
    data: {
      decision: "approve",
      payout: 1500,
      reason: "Covered by the wording.",
      section: "2. Trip Cancellation and Interruption",
    },
  });
  return claim_id;
}

test("the queue lists the claims and opens one in full", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Claims queue" }),
  ).toBeVisible();
  await expect(page.locator("table.queue tbody tr")).toHaveCount(25);
  await page.getByRole("link", { name: "CLM-1001" }).click();
  await expect(page.getByRole("heading", { name: "CLM-1001" })).toBeVisible();
  await expect(
    page.getByText(/canceled by Meridian Air/).first(),
  ).toBeVisible();
  await expect(page.getByText("Hotel receipt")).toBeVisible();
});

test("a handler signs off and pays a claim, by keyboard alone", async ({
  page,
  request,
}) => {
  const claimId = await claimWaitingForSignOff(request);
  await page.goto(`/#/claims/${claimId}`);
  await expect(page.getByText("Waiting for sign-off").first()).toBeVisible();
  const button = page.getByRole("button", { name: "Sign off and pay" });
  await expect(page.getByRole("combobox", { name: "Handler" })).toHaveValue(
    "HND-01",
  );
  await page.getByRole("combobox", { name: "Handler" }).focus();
  await page.keyboard.press("Tab");
  await expect(button).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(
    page.getByText("Paid $1,500.00 after sign-off by Dana Whitfield"),
  ).toBeVisible();
  await expect(page.getByText("Decided").first()).toBeVisible();
});

test("the queue's links can be followed by keyboard", async ({ page }) => {
  await page.goto("/");
  const link = page.getByRole("link", { name: "CLM-1001" });
  await link.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "CLM-1001" })).toBeVisible();
});

/** Open a page in a theme and return what axe finds against WCAG 2.2 AA. */
async function violations(page: Page, path: string, theme: string) {
  await page.addInitScript((saved) => {
    localStorage.setItem("theme", saved);
  }, theme);
  await page.goto(path);
  await expect(page.locator("main h1")).toBeVisible();
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
    .analyze();
  return results.violations;
}

for (const theme of ["dark", "light"]) {
  for (const path of ["/", "/#/claims/CLM-1001", "/#/instructions"]) {
    test(`no accessibility violations on ${path} in ${theme} mode`, async ({
      page,
    }) => {
      expect(await violations(page, path, theme)).toEqual([]);
    });
  }

  test(`no accessibility violations on the sign-off form in ${theme} mode`, async ({
    page,
    request,
  }) => {
    const claimId = await claimWaitingForSignOff(request);
    expect(await violations(page, `/#/claims/${claimId}`, theme)).toEqual([]);
  });
}
