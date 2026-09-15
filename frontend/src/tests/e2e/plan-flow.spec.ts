import { expect, test } from "@playwright/test";

test("plan flow: request -> three costed options", async ({ page }) => {
  await page.goto("/plan");

  // JAC (Jackson Hole) sits right next to the seeded Grand Teton spot — close enough
  // to be a real candidate under the planner's drive-radius filter.
  await page.getByLabel("Departure airport (3-letter code)").fill("JAC");
  await page.getByLabel("Start date").fill("2026-10-05");
  await page.getByLabel("End date").fill("2026-10-09");

  await page.getByRole("button", { name: "Plan my trip" }).click();

  await expect(page).toHaveURL(/\/plan\/[^/]+$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Your trip options" })).toBeVisible();

  await expect(page.getByRole("heading", { name: "Lean" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Balanced" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Comfort" })).toBeVisible();

  // Each option shows a real, non-zero total cost (a $0.00 figure would mean the
  // costing engine silently produced nothing).
  const totals = await page.locator("span.figure.text-xl").allTextContents();
  expect(totals).toHaveLength(3);
  for (const total of totals) {
    expect(total).toMatch(/\$[1-9]/);
  }
});
