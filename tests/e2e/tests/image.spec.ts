import { test, expect } from "@playwright/test";

test.describe("image", () => {
	const TYPE = "image";
	const COMPONENT_LOCATOR = `div.CoreImage.component`;
	let url: string;

	test.beforeAll(async ({request}) => {
		const response = await request.post(`/preset/section`);
		expect(response.ok()).toBeTruthy();
		({url} = await response.json());
	});

	test.afterAll(async ({request}) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, {waitUntil: "domcontentloaded"});
	});

	test("configure", async ({ page }) => {
		await page
			.locator(`.BuilderSidebarToolkit [data-component-type="${TYPE}"]`)
			.dragTo(page.locator(".CoreSection .ChildlessPlaceholder"));
		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator('.BuilderFieldsText[data-automation-key="caption"] input')
			.fill("Hello, World!");
		await expect(page.locator(COMPONENT_LOCATOR)).toContainText(
			"Hello, World!",
		);
	});
});
