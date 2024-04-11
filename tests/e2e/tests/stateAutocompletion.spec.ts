
import { test, expect } from "@playwright/test";

const setTextField = async (page, text) => {
	await page.locator('div.CoreText.component').click();
	await page
		.locator('.BuilderFieldsText[data-automation-key="text"] .templateInput')
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
		await page.goto(url);
	});

	test.describe("text", () => {
		test("completion", async ({ page }) => {
			await setTextField(page, "@{types.");
			page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.prop:text-matches("string")').click();
			await expect(page
				.locator('.BuilderFieldsText[data-automation-key="text"] .templateInput'))
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
				.locator('.BuilderFieldsText[data-automation-key="useMarkdown"] .templateInput')
				.focus();
			await expect(page.locator('.BuilderFieldsText[data-automation-key="useMarkdown"] datalist option[value="yes"]')).toHaveCount(1);
			await expect(page.locator('.BuilderFieldsText[data-automation-key="useMarkdown"] datalist option[value="no"]')).toHaveCount(1);
		})
	});

	test.describe("Key-Value", () => {
		test("Static List - completion", async ({ page }) => {
			const FIELD = `.BuilderFieldsOptions[data-automation-key="options"]`;
			await page
				.locator(`div.component.button[data-component-type="radioinput"]`)
				.dragTo(page.locator(".CorePage"));

			await page.locator('div.CoreRadioInput.component .mainLabel').click();
			await page
				.locator(`${FIELD} button.chip:text-matches("Static List")`)
				.click();
			await page
				.locator(`${FIELD} .inputKey .templateInput`)
				.fill("@{types.");
			await expect(page.locator(`${FIELD} .inputKey .fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(page.locator(`${FIELD} .inputKey .fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			page.locator(`${FIELD} .inputKey .fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(page
				.locator(`${FIELD} .inputKey .templateInput`))
				.toHaveValue("@{types.string");
			await page
				.locator(`${FIELD} .inputValue .templateInput`)
				.fill("@{types.");
			await expect(page.locator(`${FIELD} .inputValue .fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(page.locator(`${FIELD} .inputValue .fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			page.locator(`${FIELD} .inputValue .fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(page
				.locator(`${FIELD} .inputValue .templateInput`))
				.toHaveValue("@{types.string");
			await page.locator('[data-automation-action="delete"]').click();
		});

		test("JSON - completion", async ({ page }) => {
			const FIELD = `.BuilderFieldsOptions[data-automation-key="options"]`;
			await page
				.locator(`div.component.button[data-component-type="radioinput"]`)
				.dragTo(page.locator(".CorePage"));

			await page.locator('div.CoreRadioInput.component .mainLabel').click();
			await page
				.locator(`${FIELD} button.chip:text-matches("JSON")`)
				.click();
			await page
				.locator(`${FIELD} .templateInput`)
				.fill("@{types.");
			await expect(page.locator(`${FIELD} .fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(page.locator(`${FIELD} .fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			page.locator(`${FIELD} .fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(page
				.locator(`${FIELD} .templateInput`))
				.toHaveValue("@{types.string");
			await page.locator('[data-automation-action="delete"]').click();
		});
	});

	function testFieldType(type, key, componentSelector) {
		test(`${type} field - state completion`, async ({ page }) => {
			const FIELD = `.${type}[data-automation-key="${key}"]`; 
			await page.locator(componentSelector).click();
			await page
				.locator(`${FIELD} button.chip:text-matches("CSS")`)
				.click();
			await page
				.locator(`${FIELD} .templateInput`)
				.fill("@{types.");
			await expect(page.locator(`${FIELD} .fieldStateAutocomplete span.prop`)).toHaveText(["none", "string", "integer", "float"]);
			await expect(page.locator(`${FIELD} .fieldStateAutocomplete span.type`)).toHaveText(["null", "string", "number", "number"]);
			page.locator(`${FIELD} .fieldStateAutocomplete span.prop:text-matches("string")`).click();
			await expect(page
				.locator(`${FIELD} .templateInput`))
				.toHaveValue("@{types.string");
		});
	}

	testFieldType("BuilderFieldsColor", "primaryTextColor", 'div.CoreText.component');
	testFieldType("BuilderFieldsShadow", "buttonShadow", '.BuilderTreeBranch [data-branch-component-type="root"]');
	testFieldType("BuilderFieldsAlign", "contentHAlign", '.BuilderTreeBranch [data-branch-component-type="root"]');
	testFieldType("BuilderFieldsPadding", "contentPadding", '.BuilderTreeBranch [data-branch-component-type="root"]');
	testFieldType("BuilderFieldsWidth", "contentWidth", '.BuilderTreeBranch [data-branch-component-type="root"]');
});
