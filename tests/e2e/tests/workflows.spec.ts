import { test, expect } from "@playwright/test";

const setTextField = async (page, text) => {
	await page.locator('div.CoreText.component').click();
	await page
		.locator('.BuilderFieldsText[data-automation-key="text"] .templateInput')
		.fill(text);
}

test.describe("Workflows", () => {
	let url: string;

	test.beforeAll(async ({request}) => {
		const response = await request.post(`/preset/workflows`);
		expect(response.ok()).toBeTruthy();
		({url} = await response.json());
	});

	test.afterAll(async ({request}) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url);
	});

	test.describe("Payload and context", () => {

		const instancePaths = ["root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,ixxb26ukbvr0sknw:0,iftqnmjw8ipaknex:0,7no34ag7gmwgm1rd:0", "root:0,c0f99a9e-5004-4e75-a6c6-36f17490b134:0,ixxb26ukbvr0sknw:0,iftqnmjw8ipaknex:0,7no34ag7gmwgm1rd:0"];

		test("completion", async ({ page }) => {
			page.locator('.BuilderFieldsText[data-automation-key="text"] .fieldStateAutocomplete span.prop:text-matches("string")').click();
			
			await setTextField(page, "@{types.");
			await expect(page
				.locator('.BuilderFieldsText[data-automation-key="text"] .templateInput'))
				.toHaveValue("@{types.string");
		});

	});

});