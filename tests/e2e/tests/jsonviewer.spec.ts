import { test, expect } from "@playwright/test";

test.describe("JSON viewer", () => {
	let url: string;

	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/jsonviewer`);
		expect(response.ok()).toBeTruthy();
		({ url } = await response.json());
	});

	test.afterAll(async ({ request }) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, {waitUntil: "domcontentloaded"});
		test.setTimeout(5000);
	});

	test("should controle the depth open", async ({ page }) => {
		await page.locator(".CoreJsonViewer").click();
		await page.locator(".BuilderTemplateInput").first().click();

		expect(await page.locator(".CoreJsonViewer details[open]").count()).toBe(0);

		await page.getByRole("combobox").first().fill("1");
		expect(await page.locator(".CoreJsonViewer details[open]").count()).toBe(1);

		await page.getByRole("combobox").first().fill("-1");
		expect(await page.locator(".CoreJsonViewer details[open]").count()).toBe(5);
	});
});
