import { test, expect } from "@playwright/test";

test.describe("Builder field validation", () => {
	let url: string;

	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/section`);
		expect(response.ok()).toBeTruthy();
		({ url } = await response.json());
	});

	test.afterAll(async ({ request }) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, { waitUntil: "domcontentloaded" });
		test.setTimeout(5000);
		await page.locator(`[data-automation-action="set-mode-ui"]`).click();
	});

	test("should display error for invalid button fields", async ({ page }) => {
		await page.locator(`[data-automation-action="sidebar-add"]`).click();
		await page
			.locator(`.BuilderSidebarToolkit [data-component-type="button"]`)
			.dragTo(page.locator(".CoreSection"));
		await page.locator(`button.CoreButton.component`).click();

		// css classes
		const fieldWrapper = page.locator(
			'.BuilderFieldsText[data-automation-key="cssClasses"]',
		);
		const field = fieldWrapper.locator(".BuilderTemplateInputInput");
		const fieldEditable = field.locator(".StateWithPill");
		await fieldEditable.fill("1234");

		expect(await field.getAttribute("aria-invalid")).toBe("true");

		await fieldEditable.fill("class1 class2");
		expect(await field.getAttribute("aria-invalid")).toBe("false");
	});

	test("should display error for invalid multiselectinput fields", async ({
		page,
	}) => {
		await page.locator(`[data-automation-action="sidebar-add"]`).click();
		await page
			.locator(
				`.BuilderSidebarToolkit [data-component-type="multiselectinput"]`,
			)
			.dragTo(page.locator(".CoreSection"));
		await page.locator(`.CoreMultiselectInput.component`).click();

		// maximum count

		const fieldWrapper = page.locator(
			'.BuilderFieldsText[data-automation-key="maximumCount"]',
		);
		const field = fieldWrapper.locator(".BuilderTemplateInputInput");
		const fieldEditable = field.locator(".StateWithPill");
		await fieldEditable.fill("1234");

		await fieldEditable.fill("-1");
		expect(await field.getAttribute("aria-invalid")).toBe("true");

		await fieldEditable.fill("2");
		expect(await field.getAttribute("aria-invalid")).toBe("false");
	});
});
