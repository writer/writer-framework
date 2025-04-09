import { test, expect, type Page } from "@playwright/test";

test.describe('undo and redo', () => {
	const TYPE = 'button';
	const COMPONENT_LOCATOR = 'button.CoreButton.component';
	const COLUMN1 = ".CoreColumns .CoreColumn:nth-child(1 of .CoreColumn)";
	const COLUMN2 = ".CoreColumns .CoreColumn:nth-child(2 of .CoreColumn)";
	let url: string;

	const collapseSettingsBar = async (page: Page) => {
		await page.locator('.BuilderSettings button[data-automation-action="collapse-settings"]').click();
	}

	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/2columns`);
		expect(response.ok()).toBeTruthy();
		({ url } = await response.json());
	});

	test.afterAll(async ({ request }) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, {waitUntil: "domcontentloaded"});
	});

	test("create, drag and drop, property change and remove", async ({ page }) => {
		await page
			.locator(`.BuilderSidebarToolkit [data-component-type="${TYPE}"]`)
			.dragTo(page.locator(COLUMN1));
		await page.locator('.BuilderHeader [data-automation-key="undo"]').click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0)
		await page.locator('.BuilderHeader [data-automation-key="redo"]').click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(1)

		await page.locator(COMPONENT_LOCATOR).dragTo(page.locator(COLUMN2));
		await page.locator('.BuilderHeader [data-automation-key="undo"]').click();
		await expect(
			page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
		).toHaveCount(1);
		await expect(
			page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
		).toHaveCount(0);
		await page.locator('.BuilderHeader [data-automation-key="redo"]').click();
		await expect(
			page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
		).toHaveCount(0);
		await expect(
			page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
		).toHaveCount(1);

		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator('.BuilderFieldsText[data-automation-key="text"] input')
			.fill('cool text');
		await collapseSettingsBar(page);
		await page.locator('.BuilderHeader [data-automation-key="undo"]').click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveText('Button Text')
		await page.locator('.BuilderHeader [data-automation-key="redo"]').click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveText('cool text')

		await page.locator(COMPONENT_LOCATOR).click();
		await page
			.locator(
				'.BuilderSettingsActions .actionButton[data-automation-action="delete"]',
			)
			.click();
		await page.locator('.BuilderHeader [data-automation-key="undo"]').click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(1)
		await page.locator('.BuilderHeader [data-automation-key="redo"]').click();
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0)
	});
});
