import { test, expect } from "@playwright/test";

test.describe("sidebar", () => {
	let url: string;

	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/empty_page`);
		expect(response.ok()).toBeTruthy();
		({ url } = await response.json());
	});

	test.afterAll(async ({ request }) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url);
		test.setTimeout(5000);
	});

	test.describe("Toolkit", () => {
		test("should filter", async ({ page }) => {
			// click on icon to begin search
			await page
				.locator(
					`.BuilderSidebarToolbar .BuilderSidebarTitleSearch [data-automation-action="search"]`,
				)
				.click();

			// search a button
			await page
				.locator(`.BuilderSidebarToolbar .BuilderSidebarTitleSearch input`)
				.fill("button");

			// should have only one result
			expect(
				await page.locator(`.BuilderSidebarToolbar .component`).count(),
			).toBe(1);

			// close search
			await page
				.locator(
					`.BuilderSidebarToolbar .BuilderSidebarTitleSearch [data-automation-action="close"]`,
				)
				.click();

			// should reset the search
			expect(
				await page.locator(`.BuilderSidebarToolbar .component`).count(),
			).not.toBe(1);
		});

		test("should be compatible with keyboard navigation", async ({ page }) => {
			// click on icon to begin search
			await page
				.locator(
					`.BuilderSidebarToolbar .BuilderSidebarTitleSearch [data-automation-action="search"]`,
				)
				.click();

			// search a button
			await page
				.locator(`.BuilderSidebarToolbar .BuilderSidebarTitleSearch input`)
				.fill("button");

			// should have only one result
			expect(
				await page.locator(`.BuilderSidebarToolbar .component`).count(),
			).toBe(1);

			await page.keyboard.press("Tab");
			await page.keyboard.press("Enter");

			// should reset the search
			expect(
				await page.locator(`.BuilderSidebarToolbar .component`).count(),
			).not.toBe(1);
		});
	});
});
