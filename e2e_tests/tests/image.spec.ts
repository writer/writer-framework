import { test, expect } from "@playwright/test";

test.describe("image", () => {
	const TYPE = "image";
	const COMPONENT_LOCATOR = `div.CoreImage.component`;

	test.beforeAll(async ({request}) => {
		const response = await request.get(`/preset/section`);
		expect(response.ok()).toBeTruthy();
	});

	test.beforeEach(async ({ page }) => {
		await page.goto("/");
	});

	test("configure", async ({ page }) => {
		await page
			.locator(`div.component.button[data-component-type="${TYPE}"]`)
			.dragTo(page.locator(".CoreSection .ChildlessPlaceholder"));
		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator('.BuilderFieldsText[data-key="caption"] input')
			.fill("Hello, World!");
		await expect(page.locator(COMPONENT_LOCATOR)).toContainText(
			"Hello, World!",
		);
	});
});
