import { test, expect } from "@playwright/test";

const createAndRemove = [
	{ type: "sidebar", locator: `div.CoreSidebar.component` },
	{ type: "section", locator: `section.CoreSection.component` },
	{ type: "columns", locator: `div.CoreColumns.component` },
];


createAndRemove.forEach(({ type, locator }) => {
	test.describe(type, () => {
		const TYPE = type;
		const COMPONENT_LOCATOR = locator;
		const TARGET = ".CorePage";
		let url: string;

		test.beforeAll(async ({request}) => {
			const response = await request.post(`/preset/empty_page`);
			expect(response.ok()).toBeTruthy();
			({url} = await response.json());
		});

		test.afterAll(async ({request}) => {
			await request.delete(url);
		});

		test.beforeEach(async ({ page }) => {
			await page.goto(url);
		});

		test("create and remove", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(TARGET));
			await expect(
				page.locator(TARGET + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);

			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});
	});
});

