import { test, expect } from "@playwright/test";

test.describe("Workflows", () => {
	let url: string;

	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/workflows`);
		expect(response.ok()).toBeTruthy();
		({ url } = await response.json());
	});

	test.afterAll(async ({ request }) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url, {waitUntil: "domcontentloaded"});
	});

	const inputData = [
		{ object: "plant", color: "green" },
		{ object: "cup", color: "pink" },
	];

	for (const { object, color } of inputData) {
		test(`Test context and payload in Workflows for ${object} ${color}`, async ({
			page,
		}) => {
			await page.getByPlaceholder(object).fill(color);
			await page.locator(`[data-automation-action="toggle-panel"][data-automation-key="log"]`).click();
			const rowsLocator = page
				.locator(".BuilderPanelSwitcher div.row");
			await expect(rowsLocator).toHaveCount(3);
			const rowLocator = rowsLocator.filter({ hasText: "Return value" });
			await rowLocator.getByRole("button", { name: "Details" }).click();
			await expect(page.locator(".BuilderModal")).toBeVisible();
			const resultsLocator = page.locator(
				`.BuilderModal [data-automation-key="result"]`,
			);
			const returnValueLocator = page.locator(
				`.BuilderModal [data-automation-key="return-value"]`,
			);
			const expectedTexts = ["color", color, "object", object];
			for (const text of expectedTexts) {
				await expect(resultsLocator).toContainText(text);
				await expect(returnValueLocator).toContainText(text);
			}
		});
	}

	test("Create workflow and run workflow repeat_payload from it", async ({
		page,
	}) => {
		await page.locator(`[data-automation-action="set-mode-workflows"]`).click();
		await page.locator(`[data-automation-action="add-workflow"]`).click();

		await page
			.locator(
				`.BuilderSidebarToolkit [data-component-type="workflows_runworkflow"]`,
			)
			.dragTo(page.locator(".WorkflowsWorkflow"), {
				targetPosition: { x: 100, y: 100 },
			});
		const runWorkflowBlock = page.locator(`.WorkflowsNode.wf-type-workflows_runworkflow`);

		await page
			.locator(
				`.BuilderSidebarToolkit [data-component-type="workflows_returnvalue"]`,
			)
			.dragTo(page.locator(".WorkflowsWorkflow"), {
				targetPosition: { x: 400, y: 100 },
			});
		const returnValueBlock = page.locator(`.WorkflowsNode.wf-type-workflows_returnvalue`);

		await runWorkflowBlock.click();
		await page.locator(`.BuilderFieldsText[data-automation-key="workflowKey"] input`).fill("repeat_payload");
		const payload = "blue";
		await page.locator(`.BuilderFieldsText[data-automation-key="payload"] textarea`).fill(payload);
		await page.locator(`[data-automation-action="collapse-settings"]`).click();

		await runWorkflowBlock.locator(".ball.success").dragTo(returnValueBlock);

		await returnValueBlock.click();
		await page.locator(`.BuilderFieldsText[data-automation-key="value"] textarea`).fill("@{result}");

		await page.locator(`[data-automation-action="run-workflow"]`).click();

		await page.locator(`[data-automation-action="toggle-panel"][data-automation-key="log"]`).click();
		const rowsLocator = page.locator(".BuilderPanelSwitcher div.row");
		await expect(rowsLocator).toHaveCount(3);
		const rowLocator = rowsLocator.filter({ hasText: "Return value" }).first();;
		await rowLocator.getByRole("button", { name: "Details" }).click();
		await expect(page.locator(".BuilderModal")).toBeVisible();
		const returnValueLocator = page.locator(
			`.BuilderModal [data-automation-key="return-value"]`,
		);
		await expect(returnValueLocator).toContainText("blue");
	});
});