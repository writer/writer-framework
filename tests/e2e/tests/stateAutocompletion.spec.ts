import { test, expect } from "@playwright/test";

const setTextField = async (page, text) => {
	await page.locator("div.CoreText.component").click();
	await page
		.locator('.BuilderFieldsText[data-automation-key="text"]')
		.locator('[data-automation-key="template-editor"]')
		.fill(text);
};

test.describe("state autocompletion", () => {
	let url: string;
	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/state`);
		expect(response.ok()).toBeTruthy();
		({ url } = await response.json());
	});

	test.afterAll(async ({ request }) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, { waitUntil: "domcontentloaded" });
		await page.locator(`[data-automation-action="set-mode-ui"]`).click();
	});

	test.describe("text", () => {
		test("completion", async ({ page }) => {
			await setTextField(page, "@{types.");

			const field = page.locator(
				'.BuilderFieldsText[data-automation-key="text"]',
			);

			field
				.locator('.WdsDropdownMenuItem[data-automation-key="types.string"]')
				.click();
			await expect(
				field.locator('[data-automation-key="template-editor"]'),
			).toHaveText("@{types.string}");
		});
		test("counter", async ({ page }) => {
			await setTextField(page, "@{counter");
			const field = page.locator(
				'.BuilderFieldsText[data-automation-key="text"]',
			);
			await expect(field.locator(".WdsDropdownMenuItem")).toContainText([
				"counter",
			]);
		});

		test("deeply nested", async ({ page }) => {
			await setTextField(page, "@{nested.c.");
			const field = page.locator(
				'.BuilderFieldsText[data-automation-key="text"]',
			);
			await expect(field.locator(".WdsDropdownMenuItem")).toContainText([
				"d",
				"e",
			]);
		});
	});

	test.describe.skip("checkbox field", () => {
		test("checkbox should toggle on click and have correct label", async ({
			page,
		}) => {
			await page.locator("div.CoreText.component").click();

			const field = page.locator(
				'.BuilderFieldsCheckbox[data-automation-key="useMarkdown"]',
			);

			const checkbox = field.locator(".WdsCheckbox");

			await expect(checkbox).toHaveCount(1);

			await expect(checkbox).not.toHaveClass(/WdsCheckbox--checked/);
			await checkbox.click();
			await expect(checkbox).toHaveClass(/WdsCheckbox--checked/);
		});
	});

	test.describe.skip("Key-Value", () => {
		test("Static List - completion", async ({ page }) => {
			await page.locator(`[data-automation-action="sidebar-add"]`).click();
			const FIELD = `.BuilderFieldsKeyValue[data-automation-key="options"]`;
			await page
				.locator(`.BuilderSidebarToolkit [data-component-type="radioinput"]`)
				.dragTo(page.locator(".CorePage"));

			await page.locator("div.CoreRadioInput.component > label").click();
			await page
				.locator(`${FIELD} button[data-automation-key="openAssistedMode"]`)
				.click();

			// key

			const assistedKeyField = page
				.locator(
					`.BuilderFieldsKeyValueModal__assistedEntries .WdsFieldWrapper`,
				)
				.first();
			const assistedKeyFieldInput = assistedKeyField.locator(".WdsTextInput");

			await assistedKeyFieldInput.fill("@{types.");

			await expect(
				assistedKeyField.locator(`.WdsDropdownMenuItem__label`),
			).toHaveText([
				"types.float",
				"types.integer",
				"types.none",
				"types.string",
			]);
			await assistedKeyField
				.locator('[data-automation-key="types.string"]')
				.click();
			await expect(assistedKeyFieldInput).toHaveValue("@{types.string}");

			// value

			const assistedValueField = page
				.locator(
					`.BuilderFieldsKeyValueModal__assistedEntries .WdsFieldWrapper`,
				)
				.nth(1);
			const assistedKeyValueInput = assistedValueField.locator(".WdsTextInput");

			await assistedKeyValueInput.fill("@{types.");
			await expect(
				assistedValueField.locator(`.WdsDropdownMenuItem__label`),
			).toHaveText([
				"types.float",
				"types.integer",
				"types.none",
				"types.string",
			]);
			await assistedValueField
				.locator('[data-automation-key="types.string"]')
				.click();
			await expect(assistedKeyValueInput).toHaveValue("@{types.string}");
		});
	});

	function testFieldType(type, key, componentSelector) {
		test(`${type} field - state completion`, async ({ page }) => {
			await page.locator(`[data-automation-action="sidebar-layers"]`).click();
			const FIELD = `.${type}[data-automation-key="${key}"]`;
			const field = page.locator(`.${type}[data-automation-key="${key}"]`);
			await page.locator(componentSelector).click();
			await field.locator(`button.WdsTab:text-matches("CSS")`).click();
			await field
				.locator(`.BuilderTemplateInput`)
				.locator('[data-automation-key="template-editor"]')
				.fill("@{types.");
			await expect(field.locator(`.WdsDropdownMenuItem__label`)).toHaveText([
				"types.float",
				"types.integer",
				"types.none",
				"types.string",
			]);
			field.locator('[data-automation-key="types.string"]').click();
			await expect(
				field
					.locator(`.BuilderTemplateInput`)
					.locator('[data-automation-key="template-editor"]'),
			).toHaveText("@{types.string}");
		});
	}

	testFieldType(
		"BuilderFieldsColor",
		"primaryTextColor",
		"div.CoreText.component",
	);
	testFieldType(
		"BuilderFieldsShadow",
		"buttonShadow",
		'.BuilderSidebarComponentTree [data-automation-key="root"]',
	);
	testFieldType(
		"BuilderFieldsAlign",
		"contentHAlign",
		'.BuilderSidebarComponentTree [data-automation-key="root"]',
	);
	testFieldType(
		"BuilderFieldsPadding",
		"contentPadding",
		'.BuilderSidebarComponentTree [data-automation-key="root"]',
	);
	testFieldType(
		"BuilderFieldsWidth",
		"contentWidth",
		'.BuilderSidebarComponentTree [data-automation-key="root"]',
	);
});
