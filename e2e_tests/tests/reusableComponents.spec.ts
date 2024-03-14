import { test, expect } from "@playwright/test";

test.describe("Reusable component", () => {
	const TYPE = "reusable";
	const COMPONENT_LOCATOR = `div.CoreReuse.component`;

	const fillSettingsField = async (page, key, value) => {
		await page
			.locator(`.BuilderFieldsText[data-key="${key}"] input, .BuilderFieldsText[data-key="${key}"] textarea`)
			.fill(value);
	}

	const dragNewComponent = async (page, type, where = ".CoreSection") => {
			await page
				.locator(`div.component.button[data-component-type="${type}"]`)
				.dragTo(page.locator(where));
	}

	const getSelectedComponentId = async (page) => {
		return await page.locator('.BuilderSettings .copyText').innerText();
	}

	const setReuseTarget = async (page, id) => {
		await page.locator(COMPONENT_LOCATOR).click();
		await fillSettingsField(page, "proxyId", id);
	};

	const createReuseable = async (page, where = '.CoreSection') => {
		await dragNewComponent(page, TYPE, where);
		await page.locator(COMPONENT_LOCATOR).click();
		return await getSelectedComponentId(page);
	};

	const createText = async (page, where = ".CoreSection") => {
		await dragNewComponent(page, "text", where);
		await page.locator('.CoreText.component').click();
		await fillSettingsField(page, "text", "Hello, World!");
		return await getSelectedComponentId(page);
	};

	const createSidebar = async (page) => {
		dragNewComponent(page, "sidebar", ".CorePage");
		await page.locator('.CoreSidebar.component').click();
		return await getSelectedComponentId(page);
	};

	const removeComponent = async (page, locator) => {
		await page.locator(".CorePage").click();
		await page.locator(locator).click();
		await page
			.locator(
				'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
			)
			.click();
		await expect(page.locator(locator)).not.toBeVisible();
		await expect(page.locator(locator)).toHaveCount(0);
	};

	test.describe("basic", () => {
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
			await page.goto(url);
		});

		test.afterEach(async ({ page }) => {
			await removeComponent(page, '.CoreReuse');
		});

		test("empty info", async ({page}) => {
			await createReuseable(page);
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveClass(/empty/);
		});

		test("reuse text component", async ({ page }) => {
			const id = await createText(page);
			await createReuseable(page);
			await setReuseTarget(page, id);
			await expect(page.locator('.CoreText.component')).toHaveCount(2);
			await expect(page.locator('.CoreReuse.CoreText.component')).toHaveCount(1);
		});

		test("self-referencing", async ({page}) => {
			const id = await createReuseable(page);
			await setReuseTarget(page, id);
			await expect(page.locator('.CoreReuse.component')).toHaveClass(/invalid-value/);
		});

		test("reuse in incorect context", async ({page}) => {
			const id = await createSidebar(page);
			await createReuseable(page);
			await setReuseTarget(page, id);
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveClass(/invalid-context/);
		});
	});

	test.describe("between pages", () => {
		let url: string;

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
			await page.goto(url+"#page2");
			await removeComponent(page, ".CoreReuse");
			await page.goto(url+"#page1");
			const c = await page.locator('.CoreSidebar').count();
			if (c > 0) {
				await removeComponent(page, '.CoreSidebar');
			}
		});

		test("reuse sloted component", async ({page}) => {
			await page.goto(url+"#page1");
			const id = await createSidebar(page);
			await page.goto(url+"#page2");
			await createReuseable(page, ".CorePage");
			await setReuseTarget(page, id);
			await expect(page.locator('.sidebarContainer .CoreReuse.CoreSidebar')).toHaveCount(1);
		});

		test("dynamic slot change", async ({page}) => {
			await page.goto(url+"#page1");
			const sidebarId = await createSidebar(page);
			await page.goto(url+"#page2");
			await createReuseable(page, ".CorePage");
			await setReuseTarget(page, sidebarId);
			await expect(page.locator('.sidebarContainer .CoreReuse.CoreSidebar')).toHaveCount(1);
			const textId = await createText(page, ".CorePage");
			await setReuseTarget(page, textId);
			expect(page.locator('.sidebarContainer .CoreText')).toHaveCount(0);
			expect(page.locator('.main .CoreReuse.CoreText')).toHaveCount(1);
		});

		test("target component deleted", async ({page}) => {
			await page.goto(url+"#page1");
			const sidebarId = await createSidebar(page);
			await page.goto(url+"#page2");
			await createReuseable(page, ".CorePage");
			await setReuseTarget(page, sidebarId);
			await page.goto(url+"#page1");
			await removeComponent(page, '.CoreSidebar');
			await page.goto(url+"#page2");
			await expect(page.locator('.CoreReuse.component')).toHaveClass(/invalid-value/);
		});
	});
});
