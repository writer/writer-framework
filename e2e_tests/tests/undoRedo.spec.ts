import { test, expect } from "@playwright/test";

test.setTimeout(5000);

const loadPreset = async (preset) => {
	await fetch(`http://127.0.0.1:7358/${preset}`);
};

test.describe('undo and redo', () => {
	const TYPE = 'button';
	const COMPONENT_LOCATOR = 'button.CoreButton.component';
	const COLUMN1 = ".CoreColumns .CoreColumn:nth-child(1 of .CoreColumn)";
	const COLUMN2 = ".CoreColumns .CoreColumn:nth-child(2 of .CoreColumn)";

	test.beforeAll(async ({request}) => {
		const response = await request.get(`/preset/2columns`);
		expect(response.ok()).toBeTruthy();
	});

	test.beforeEach(async ({ page }) => {
		await page.goto("/");
	});

	test("create", async ({ page }) => {
		await page
			.locator(`div.component.button[data-component-type="${TYPE}"]`)
			.dragTo(page.locator(COLUMN1));
		await page.locator("button.undo").click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0)
		await page.locator("button.redo").click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(1)
	});

	test("drag and drop", async ({ page }) => {
		await page.locator(COMPONENT_LOCATOR).dragTo(page.locator(COLUMN2));
		await page.locator("button.undo").click();
		await expect(
			page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
		).toHaveCount(1);
		await expect(
			page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
		).toHaveCount(0);
		await page.locator("button.redo").click();
		await expect(
			page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
		).toHaveCount(0);
		await expect(
			page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
		).toHaveCount(1);
	});

	test("property change", async ({ page }) => {
		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator('.BuilderFieldsText[data-key="text"] input')
			.fill('cool text');
		await page.locator("button.undo").click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveText('Button Text')
		await page.locator("button.redo").click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveText('cool text')
	});


	test("remove", async ({ page }) => {
		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator(
				'.BuilderComponentShortcuts .actionButton[data-action="delete"]',
			)
			.click();
		await page.locator("button.undo").click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(1)
		await page.locator("button.redo").click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0)
	});
});
