import { expect, test } from "@playwright/test";

test("spot pages: renders overview/cost/best-time/reservations/campervan", async ({ page }) => {
  await page.goto("/spots/zion");
  await expect(page.getByRole("heading", { name: "Zion", exact: true })).toBeVisible();

  await page.goto("/spots/zion/cost");
  await expect(page.getByRole("heading", { name: "Zion: cost breakdown" })).toBeVisible();

  await page.goto("/spots/zion/best-time-to-visit");
  await expect(page.getByRole("heading", { name: "Best time to visit Zion" })).toBeVisible();
  await expect(page.getByText("Crowds by month")).toBeVisible();
  await expect(page.getByText("Average temperature by month")).toBeVisible();

  await page.goto("/spots/zion/reservations");
  await expect(page.getByRole("heading", { name: "Reservations at Zion" })).toBeVisible();

  await page.goto("/spots/zion/campervan");
  await expect(page.getByRole("heading", { name: "Campervan access at Zion" })).toBeVisible();
});

test("spot pages: 404s for an unknown slug instead of crashing", async ({ page }) => {
  const response = await page.goto("/spots/not-a-real-park");
  expect(response?.status()).toBe(404);
});
