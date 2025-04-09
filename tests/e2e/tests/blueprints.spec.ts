import { test, expect, Locator } from "@playwright/test";

test.describe("Blueprints", () => {
	let url: string;

	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/blueprints`);
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
		test(`Test context and payload in Blueprints for ${object} ${color}`, async ({
			page,
		}) => {
			await page.getByPlaceholder(object).fill(color);
			await page
				.locator(
					`[data-automation-action="toggle-panel"][data-automation-key="log"]`,
				)
				.click();
			const rowsLocator = page.locator(
				".BuilderPanelSwitcher div.BuilderListItem",
			);
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

	test("Create blueprint and run blueprint repeat_payload from it", async ({
		page,
	}) => {
		await page.locator(`[data-automation-action="set-mode-blueprints"]`).click();
		await page.locator(`[data-automation-action="add-blueprint"]`).click();

		await page
			.locator(
				`.BuilderSidebarToolkit [data-component-type="blueprints_runblueprint"]`,
			)
			.dragTo(page.locator(".BlueprintsBlueprint"), {
				targetPosition: { x: 100, y: 100 },
			});
		const runBlueprintBlock = page.locator(
			`.BlueprintsNode.wf-type-blueprints_runblueprint`,
		);

		await page
			.locator(
				`.BuilderSidebarToolkit [data-component-type="blueprints_returnvalue"]`,
			)
			.dragTo(page.locator(".BlueprintsBlueprint"), {
				targetPosition: { x: 400, y: 100 },
			});
		const returnValueBlock = page.locator(
			`.BlueprintsNode.wf-type-blueprints_returnvalue`,
		);

		await runBlueprintBlock.click();
		await page
			.locator(`.BuilderFieldsBlueprintKey[data-automation-key="blueprintKey"]`)
			.locator(".BuilderSelect__trigger")
			.click();
		await page
			.locator(`.BuilderFieldsBlueprintKey[data-automation-key="blueprintKey"]`)
			.locator('button[data-automation-key="repeat_payload"]')
			.click();
		const payload = "blue";
		await page
			.locator(`.BuilderFieldsText[data-automation-key="payload"] textarea`)
			.fill(payload);
		await page.locator(`[data-automation-action="collapse-settings"]`).click();

		await runBlueprintBlock.locator(".ball.success").dragTo(returnValueBlock);

		await returnValueBlock.click();
		await page
			.locator(`.BuilderFieldsText[data-automation-key="value"] textarea`)
			.fill("@{result}");

		await page.locator(`[data-automation-action="run-blueprint"]`).click();

		await page
			.locator(
				`[data-automation-action="toggle-panel"][data-automation-key="log"]`,
			)
			.click();
		const rowsLocator = page.locator(
			".BuilderPanelSwitcher div.BuilderListItem",
		);
		const successRows = rowsLocator
			.locator(".outcome")
			.filter({ hasText: "success" });
		await expect(successRows).toHaveCount(3);
		const rowLocator = rowsLocator.filter({ hasText: "Return value" }).last();
		await rowLocator.getByRole("button", { name: "Trace" }).click();
		await expect(page.locator(".WdsModal")).toBeVisible();
		const returnValueLocator = page.locator(
			`.WdsModal [data-automation-key="return-value"]`,
		);
		await expect(returnValueLocator).toContainText("blue");
	});

	test.describe("multiple selection", () => {
		let runBlueprintBlock: Locator;
		let returnValueBlock: Locator;

		test.beforeEach(async ({ page }) => {
			await page
				.locator(`[data-automation-action="set-mode-blueprints"]`)
				.click();
			await page.locator(`[data-automation-action="add-blueprint"]`).click();

			await page
				.locator(
					`.BuilderSidebarToolkit [data-component-type="blueprints_runblueprint"]`,
				)
				.dragTo(page.locator(".BlueprintsBlueprint"), {
					targetPosition: { x: 100, y: 100 },
				});
			runBlueprintBlock = page.locator(
				`.BlueprintsNode.wf-type-blueprints_runblueprint`,
			);

			await page
				.locator(
					`.BuilderSidebarToolkit [data-component-type="blueprints_returnvalue"]`,
				)
				.dragTo(page.locator(".BlueprintsBlueprint"), {
					targetPosition: { x: 400, y: 100 },
				});
			returnValueBlock = page.locator(
				`.BlueprintsNode.wf-type-blueprints_returnvalue`,
			);

			await expect(page.locator(`.BlueprintsNode`)).toHaveCount(2);

			await runBlueprintBlock.click();
			await returnValueBlock.click({ modifiers: ["Shift"] });

			await expect(page.locator(`.BlueprintsNode.selected`)).toHaveCount(2);
		});

		test("clear selection", async ({ page }) => {
			await page
				.locator(
					'.BuilderSettingsActions [data-automation-action="clear-selection"]',
				)
				.click();

			await expect(page.locator(`.BlueprintsNode.selected`)).toHaveCount(0);
		});

		test("remove multiple elements", async ({ page }) => {
			await page
				.locator('.BuilderSettingsActions [data-automation-action="delete"]')
				.click();

			await expect(page.locator(`.BlueprintsNode`)).toHaveCount(0);
		});

		test("drag multiple elements", async ({ page }) => {
			const returnValueBlockBoundingBefore =
				await returnValueBlock.boundingBox();

			await runBlueprintBlock.click();
			await returnValueBlock.click({ modifiers: ["Shift"] });

			await expect(page.locator(`.BlueprintsNode.selected`)).toHaveCount(2);

			await runBlueprintBlock.dragTo(page.locator(".BlueprintsBlueprint"), {
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
