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
		await page.goto(url, { waitUntil: "domcontentloaded" });
		test.setTimeout(5000);
	});

	test.describe("Toolkit", () => {
		test("should filter", async ({ page }) => {
			await page.locator(`[data-automation-action="sidebar-add"]`).click();
			// click on icon to begin search
			await page.locator(`.BuilderSidebarToolkit input`).click();

			// search a button
			await page.locator(`.BuilderSidebarToolkit input`).fill("button");

			// should have only one result
			expect(await page.locator(`.BuilderSidebarToolkit .tool`).count()).toBe(
				1,
			);

			// search a button
			await page.locator(`.BuilderSidebarToolkit input`).fill("");

			// should reset the search
			expect(
				await page.locator(`.BuilderSidebarToolkit .tool`).count(),
			).not.toBe(1);
		});
	});
});
