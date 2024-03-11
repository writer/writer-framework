import { test, expect } from "@playwright/test";

test.describe("button", () => {
	const TYPE = "button";
	const COMPONENT_LOCATOR = `button.CoreButton.component`;

	test.beforeAll(async ({request}) => {
		const response = await request.get(`/preset/section`);
		expect(response.ok()).toBeTruthy();
	});

	test.beforeEach(async ({ page }) => {
		await page.goto("/");
		test.setTimeout(5000);
	});

	test("configure", async ({ page }) => {
		await page
			.locator(`div.component.button[data-component-type="${TYPE}"]`)
			.dragTo(page.locator(".CoreSection .ChildlessPlaceholder"));
		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator('.BuilderFieldsText[data-key="text"] input')
			.fill("Hello, World!");
		await expect(page.locator(COMPONENT_LOCATOR)).toContainText(
			"Hello, World!",
		);
	});
});
