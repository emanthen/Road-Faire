import { expect, test } from "@playwright/test";

test("fee calculator: non-resident surcharge vs pass recommendation", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Grand Canyon", exact: true }).click();
  await page.getByRole("radio", { name: "Non-resident" }).click();

  await page.getByRole("button", { name: "Calculate" }).click();

  await expect(page.getByText("Paying as you go", { exact: true })).toBeVisible();
  await expect(page.getByText("Annual pass", { exact: true })).toBeVisible();

  // The recommendation sentence's exact wording depends on which option wins (see
  // apps.fees.explain.explain_recommendation), but every branch cites a dollar
  // figure — assert that rather than one specific branch's copy.
  await expect(page.locator("p.mt-4.text-ink")).toContainText(/\$\d/);
});
