
import { test, expect } from "@playwright/test";

const setTextField = async (page, text) => {
	await page.locator('div.CoreText.component').click();
	await page
		.locator('.BuilderFieldsText[data-automation-key="text"] textarea')
		.fill(text);
}

test.describe("state autocompletion", () => {
	let url: string;
	test.beforeAll(async ({request}) => {
		const response = await request.post(`/preset/state`);
		expect(response.ok()).toBeTruthy();
		({url} = await response.json());
	});

	test.afterAll(async ({request}) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, {waitUntil: "domcontentloaded"});
	});

	test.describe("text", () => {
		test("completion", async ({ page }) => {
			await setTextField(page, "@{types.");
			page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.prop:text-matches("string")').click();
			await expect(page
				.locator('.BuilderFieldsText[data-automation-key="text"] textarea'))
				.toHaveValue("@{types.string");
		});
		test("counter", async ({ page }) => {
			await setTextField(page, "@{counter");
			await expect(page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.prop')).toContainText(["counter"]);
			await expect(page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.type')).toContainText(["number"]);
		});

		test("types", async ({ page }) => {
			await setTextField(page, "@{types.");
			await expect(page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.prop')).toHaveText(["none", "string", "integer", "float"]);
			await expect(page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.type')).toHaveText(["null", "string", "number", "number"]);
		});

		test("deeply nested", async ({ page }) => {
			await setTextField(page, "@{nested.c.");
			await expect(page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.prop')).toContainText(["d", "e"]);
			await expect(page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.type')).toContainText(["number", "number"]);
		});
	});

	test.describe("text with dropdown", () => {
		test("options should show on focus", async ({ page }) => {
			await page.locator('div.CoreText.component').click();
			await page
				.locator('.BuilderFieldsText[data-automation-key="useMarkdown"] input')
				.focus();
			await expect(page.locator('.BuilderFieldsText[data-automation-key="useMarkdown"] datalist option[value="yes"]')).toHaveCount(1);
			await expect(page.locator('.BuilderFieldsText[data-automation-key="useMarkdown"] datalist option[value="no"]')).toHaveCount(1);
		})
	});

	test.describe("Key-Value", () => {
		test("Static List - completion", async ({ page }) => {
			const FIELD = `.BuilderFieldsKeyValue[data-automation-key="options"]`;
			await page
				.locator(`.BuilderSidebarToolkit [data-component-type="radioinput"]`)
				.dragTo(page.locator(".CorePage"));

			await page.locator('div.CoreRadioInput.component > label').click();
			await page
				.locator(`${FIELD} button[data-automation-key="openAssistedMode"]`)
				.click();

			// key

			const assistedKeyField = page.locator(`.BuilderFieldsKeyValueModal__assistedEntries .WdsFieldWrapper`).first()
			const assistedKeyFieldInput = assistedKeyField.locator('.WdsTextInput')

			await assistedKeyFieldInput.fill("@{types.");

			await expect(assistedKeyField.locator(`.fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(assistedKeyField.locator(`.fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			await assistedKeyField.locator(`.fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(assistedKeyFieldInput).toHaveValue("@{types.string");

			// value

			const assistedValueField = page.locator(`.BuilderFieldsKeyValueModal__assistedEntries .WdsFieldWrapper`).nth(1)
			const assistedKeyValueInput = assistedValueField.locator('.WdsTextInput')

			await assistedKeyValueInput.fill("@{types.");
			await expect(assistedValueField.locator(`.fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(assistedValueField.locator(`.fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			await assistedValueField.locator(`.fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(assistedKeyValueInput).toHaveValue("@{types.string");
		});
	});

	function testFieldType(type, key, componentSelector) {
		test(`${type} field - state completion`, async ({ page }) => {
			const FIELD = `.${type}[data-automation-key="${key}"]`; 
			await page.locator(componentSelector).click();
			await page
				.locator(`${FIELD} button.WdsTab:text-matches("CSS")`)
				.click();
			await page
				.locator(`${FIELD} .BuilderTemplateInput input`)
				.fill("@{types.");
			await expect(page.locator(`${FIELD} .fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(page.locator(`${FIELD} .fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			page.locator(`${FIELD} .fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(page
				.locator(`${FIELD} .BuilderTemplateInput input`))
				.toHaveValue("@{types.string");
		});
	}

	testFieldType("BuilderFieldsColor", "primaryTextColor", 'div.CoreText.component');
	testFieldType("BuilderFieldsShadow", "buttonShadow", '.BuilderSidebarComponentTree [data-automation-key="root"]');
	testFieldType("BuilderFieldsAlign", "contentHAlign", '.BuilderSidebarComponentTree [data-automation-key="root"]');
	testFieldType("BuilderFieldsPadding", "contentPadding", '.BuilderSidebarComponentTree [data-automation-key="root"]');
	testFieldType("BuilderFieldsWidth", "contentWidth", '.BuilderSidebarComponentTree [data-automation-key="root"]');
});
