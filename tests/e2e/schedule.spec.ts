import { test, expect } from "@playwright/test";

test.describe("Homepage", () => {
  test("loads and displays the page title", async ({ page }) => {
    await page.goto("/airukan/");
    await expect(page.locator("h1")).toContainText("Today's Anime");
  });

  test("renders at least one anime card or empty state", async ({ page }) => {
    await page.goto("/airukan/");
    const cards = page.locator("article");
    const emptyState = page.getByText("No anime airing today");
    const hasCards = (await cards.count()) > 0;
    const hasEmpty = (await emptyState.count()) > 0;
    expect(hasCards || hasEmpty).toBe(true);
  });

  test("countdown element exists when anime cards are present", async ({
    page,
  }) => {
    await page.goto("/airukan/");
    const cards = page.locator("article");
    if ((await cards.count()) > 0) {
      const countdown = page.locator('[data-testid="countdown"]');
      await expect(countdown.first()).toBeVisible();
    }
  });

  test("header navigation links are visible", async ({ page }) => {
    await page.goto("/airukan/");
    await expect(page.getByRole("link", { name: "Today" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Schedule" })).toBeVisible();
  });
});

test.describe("Schedule Page", () => {
  test("loads and displays the page title", async ({ page }) => {
    await page.goto("/airukan/schedule");
    await expect(page.locator("h1")).toContainText("Weekly Schedule");
  });

  test("shows 7 day columns", async ({ page }) => {
    await page.goto("/airukan/schedule");
    const days = [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ];
    for (const day of days) {
      await expect(
        page.getByRole("heading", { name: new RegExp(day, "i") }),
      ).toBeVisible();
    }
  });

  test("can navigate from homepage to schedule", async ({ page }) => {
    await page.goto("/airukan/");
    await page.getByRole("link", { name: "Schedule" }).click();
    await expect(page).toHaveURL(/\/airukan\/schedule/);
    await expect(page.locator("h1")).toContainText("Weekly Schedule");
  });
});
