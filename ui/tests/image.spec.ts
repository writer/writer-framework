import { test, expect } from "@playwright/test";

const loadPreset = async (preset) => {
	await fetch(`http://localhost:7358/${preset}`);
};

test.describe("image", () => {
	const TYPE = "image";
	const COMPONENT_LOCATOR = `div.CoreImage.component`;

	test.beforeAll(async () => {
		await loadPreset("base");
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
