import { test, expect, Locator } from "@playwright/test";

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
		await page.goto(url, { waitUntil: "domcontentloaded" });
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
			await page
				.locator(
					`[data-automation-action="toggle-panel"][data-automation-key="log"]`,
				)
				.click();
			const rowsLocator = page.locator(".BuilderPanelSwitcher div.row");
			await expect(rowsLocator).toHaveCount(3);
			const rowLocator = rowsLocator.filter({ hasText: "Return value" });
			await rowLocator.getByRole("button", { name: "Trace" }).click();
			await expect(page.locator(".WdsModal")).toBeVisible();
			const resultsLocator = page.locator(
				`.WdsModal [data-automation-key="result"]`,
			);
			const returnValueLocator = page.locator(
				`.WdsModal [data-automation-key="return-value"]`,
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
		const runWorkflowBlock = page.locator(
			`.WorkflowsNode.wf-type-workflows_runworkflow`,
		);

		await page
			.locator(
				`.BuilderSidebarToolkit [data-component-type="workflows_returnvalue"]`,
			)
			.dragTo(page.locator(".WorkflowsWorkflow"), {
				targetPosition: { x: 400, y: 100 },
			});
		const returnValueBlock = page.locator(
			`.WorkflowsNode.wf-type-workflows_returnvalue`,
		);

		await runWorkflowBlock.click();
		await page
			.locator(`.BuilderFieldsWorkflowKey[data-automation-key="workflowKey"]`)
			.locator(".BuilderSelect__trigger")
			.click();
		await page
			.locator(`.BuilderFieldsWorkflowKey[data-automation-key="workflowKey"]`)
			.locator('button[data-automation-key="repeat_payload"]')
			.click();
		const payload = "blue";
		await page
			.locator(`.BuilderFieldsText[data-automation-key="payload"] textarea`)
			.fill(payload);
		await page.locator(`[data-automation-action="collapse-settings"]`).click();

		await runWorkflowBlock.locator(".ball.success").dragTo(returnValueBlock);

		await returnValueBlock.click();
		await page
			.locator(`.BuilderFieldsText[data-automation-key="value"] textarea`)
			.fill("@{result}");

		await page.locator(`[data-automation-action="run-workflow"]`).click();

		await page
			.locator(
				`[data-automation-action="toggle-panel"][data-automation-key="log"]`,
			)
			.click();
		const rowsLocator = page.locator(".BuilderPanelSwitcher div.row");
		await expect(rowsLocator).toHaveCount(3);
		const rowLocator = rowsLocator.filter({ hasText: "Return value" }).first();
		await rowLocator.getByRole("button", { name: "Details" }).click();
		await expect(page.locator(".BuilderModal")).toBeVisible();
		const returnValueLocator = page.locator(
			`.BuilderModal [data-automation-key="return-value"]`,
		);
		await expect(returnValueLocator).toContainText("blue");
	});

	test.describe("multiple selection", () => {
		let runWorkflowBlock: Locator;
		let returnValueBlock: Locator;

		test.beforeEach(async ({ page }) => {
			await page
				.locator(`[data-automation-action="set-mode-workflows"]`)
				.click();
			await page.locator(`[data-automation-action="add-workflow"]`).click();

			await page
				.locator(
					`.BuilderSidebarToolkit [data-component-type="workflows_runworkflow"]`,
				)
				.dragTo(page.locator(".WorkflowsWorkflow"), {
					targetPosition: { x: 100, y: 100 },
				});
			runWorkflowBlock = page.locator(
				`.WorkflowsNode.wf-type-workflows_runworkflow`,
			);

			await page
				.locator(
					`.BuilderSidebarToolkit [data-component-type="workflows_returnvalue"]`,
				)
				.dragTo(page.locator(".WorkflowsWorkflow"), {
					targetPosition: { x: 400, y: 100 },
				});
			returnValueBlock = page.locator(
				`.WorkflowsNode.wf-type-workflows_returnvalue`,
			);

			await expect(page.locator(`.WorkflowsNode`)).toHaveCount(2);

			await runWorkflowBlock.click();
			await returnValueBlock.click({ modifiers: ["Shift"] });

			await expect(page.locator(`.WorkflowsNode.selected`)).toHaveCount(2);
		});

		test("clear selection", async ({ page }) => {
			await page
				.locator(
					'.BuilderSettingsActions [data-automation-action="clear-selection"]',
				)
				.click();

			await expect(page.locator(`.WorkflowsNode.selected`)).toHaveCount(0);
		});

		test("remove multiple elements", async ({ page }) => {
			await page
				.locator('.BuilderSettingsActions [data-automation-action="delete"]')
				.click();

			await expect(page.locator(`.WorkflowsNode`)).toHaveCount(0);
		});

		test("drag multiple elements", async ({ page }) => {
			const returnValueBlockBoundingBefore =
				await returnValueBlock.boundingBox();

			await runWorkflowBlock.click();
			await returnValueBlock.click({ modifiers: ["Shift"] });

			await expect(page.locator(`.WorkflowsNode.selected`)).toHaveCount(2);

			await runWorkflowBlock.dragTo(page.locator(".WorkflowsWorkflow"), {
				targetPosition: { x: 110, y: 110 },
			});

			const returnValueBlockBounding = await returnValueBlock.boundingBox();

			expect(returnValueBlockBounding?.x).not.toBe(
				returnValueBlockBoundingBefore?.x,
			);
			expect(returnValueBlockBounding?.y).not.toBe(
				returnValueBlockBoundingBefore?.y,
			);
		});
	});
});
