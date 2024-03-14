import { test, expect } from "@playwright/test";

test.describe("Reusable component", () => {
	const TYPE = "reusable";
	const COMPONENT_LOCATOR = `div.CoreReuse.component`;
	let url: string;

	test.describe("basic", () => {
		test.beforeAll(async ({request}) => {
			const response = await request.post(`/preset/section`);
			expect(response.ok()).toBeTruthy();
			({url} = await response.json());
		});

		test.afterAll(async ({request}) => {
			await request.delete(url);
		});

		test.beforeEach(async ({ page }) => {
			await page.goto(url);
		});

		test.afterEach(async ({ page }) => {
			await page.locator(".CorePage").click();
			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).not.toBeVisible();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});

		test("empty info", async ({page}) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(".CoreSection"));

			await expect(page.locator(COMPONENT_LOCATOR)).toHaveClass(/empty/);
		});

		test("reuse text component", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="text"]`)
				.dragTo(page.locator(".CoreSection .ChildlessPlaceholder"));


			await page.locator('.CoreText.component').click();

			await page
				.locator('.BuilderFieldsText[data-key="text"] textarea')
				.fill("Hello, World!");

			const id = await page
				.locator('.BuilderSettings .copyText').innerText();

			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(".CoreSection"));


			await page.locator(COMPONENT_LOCATOR).click();

			await page
				.locator('.BuilderFieldsText[data-key="proxyId"] input')
				.fill(id);


			await expect(page.locator('.CoreText.component')).toHaveCount(2);
			await expect(page.locator('.CoreReuse.CoreText.component')).toHaveCount(1);
		});

		test("self-referencing", async ({page}) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(".CoreSection"));

			await page.locator('.CoreReuse.component').click();

			const id = await page
				.locator('.BuilderSettings .copyText').innerText();

			await page
				.locator('.BuilderFieldsText[data-key="proxyId"] input')
				.fill(id);


			await expect(page.locator('.CoreReuse.component')).toHaveClass(/invalid-value/);
		});

		test("reuse in incorect context", async ({page}) => {
			await page
				.locator(`div.component.button[data-component-type="sidebar"]`)
				.dragTo(page.locator(".CorePage"));


			await page.locator('.CoreSidebar.component').click();

			const id = await page
				.locator('.BuilderSettings .copyText').innerText();

			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(".CoreSection"));


			await page.locator(COMPONENT_LOCATOR).click();

			await page
				.locator('.BuilderFieldsText[data-key="proxyId"] input')
				.fill(id);


			await expect(page.locator(COMPONENT_LOCATOR)).toHaveClass(/invalid-context/);
		});
	});

	test.describe("between pages", () => {
		test.beforeAll(async ({request}) => {
			const response = await request.post(`/preset/2pages`);
			expect(response.ok()).toBeTruthy();
			({url} = await response.json());
		});

		test.afterAll(async ({request}) => {
			await request.delete(url);
		});

		test.beforeEach(async ({ page }) => {
			await page.goto(url);
		});

		test.afterEach(async ({ page }) => {
			await page.locator(".CorePage").click();
			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).not.toBeVisible();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});

		test("reuse sloted component", async ({page}) => {
			await page.goto(url+"#page1");
			await page
				.locator(`div.component.button[data-component-type="sidebar"]`)
				.dragTo(page.locator(".CorePage"));


			await page.locator('.CoreSidebar.component').click();

			const id = await page
				.locator('.BuilderSettings .copyText').innerText();

			await page.goto(url+"#page2");

			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(".CorePage"));


			await page.locator(COMPONENT_LOCATOR).click();

			await page
				.locator('.BuilderFieldsText[data-key="proxyId"] input')
				.fill(id);


			await expect(page.locator('.sidebarContainer .CoreReuse.CoreSidebar')).toHaveCount(1);
		});
	});
});
