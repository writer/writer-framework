import { test, expect } from "@playwright/test";
import components from "writer-ui/components.codegen.json";

const setInstruction = async (page, instruction) => {
	await page.locator("div.TestInput textarea").click();
	await page.locator("div.TestInput textarea").fill(instruction);
};

const execute = async (page) => {
	await page.locator("button.TestExec").click();
	await page.locator("button.TestExec").click();
};

function generateValue(key, field) {
	if (field.type === "Text") {
		if (key === "icon") {
			return "error-warning";
		}
		if (field.options) {
			return Object.keys(field.options)[0];
		}

		return "TEST_STRING";
	} else if (field.type === "Number") {
		return "7357";
	} else if (field.type === "Color") {
		return "#007357";
	} else if (field.type === "array") {
		return [];
	} else {
		return null;
	}
}

function generateValues(fields) {
	const values = {};
	Object.entries(fields).forEach(([key, field]) => {
		const v = generateValue(key, field);
		if (v !== null) {
			values[key] = v;
		}
	});
	return values;
}

test.describe("low-code UI", () => {
	let url: string;
	test.beforeAll(async ({ request }) => {
		const response = await request.post(`/preset/low_code`);
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

	test("init_ui -  ui initialization", async ({ page }) => {
		await expect(page.locator(`.initialization .wf-type-text`)).toHaveText(
			"Initialization successful!",
		);
	});

	components
		.filter((c) => c.category !== "Internal" && !c.deprecated)
		.forEach(({ type, internalName, fields, allowedParentTypes, toolkit }) => {
			if (toolkit && toolkit !== "core") return;
			const renderError =
				type === "root" ||
				(allowedParentTypes && !allowedParentTypes.includes("section"));

			test(`create ${type} with ui.${internalName}() inside of section ${renderError ? "- render error" : ""}`, async ({
				page,
			}) => {
				const props = generateValues(fields);
				await setInstruction(
					page,
					`
with ui.find('results'):
		ui.${internalName}(${JSON.stringify(props)})
			`,
				);
				await execute(page);

				const componentLocator = page.locator(
					`.results .wf-type-${type}.component`,
				);

				const settingsLocator = page.locator(".BuilderSettings");

				await expect(componentLocator).toHaveCount(1);

				await componentLocator.click({ force: true });

				for (const [key, value] of Object.entries(props)) {
					const fieldLocator = settingsLocator.locator(
						`div[data-automation-key="${key}"]`,
					);

					let isFieldFound = (await fieldLocator.count()) > 0;

					if (!isFieldFound) {
						const categoryTabLocator = settingsLocator.locator(
							`.WdsTabs.WdsTabs--variant-bar button`,
						);
						const categoryTabCount = await categoryTabLocator.count();

						for (let i = 0; i < Math.max(1, categoryTabCount); i++) {
							if (categoryTabCount > 0) {
								await categoryTabLocator.nth(i).click({ force: true });
								await page.waitForTimeout(100);
							}

							if ((await fieldLocator.count()) > 0) {
								isFieldFound = true;
								break;
							}
						}
					}

					expect(isFieldFound).toBe(true);
				}

				if (renderError) {
					await expect(componentLocator).toHaveClass(/RenderError/);
				} else {
					await expect(componentLocator).not.toHaveClass(/RenderError/);
				}
			});
		});
	test("settings should be enabled for bmc", async ({ page }) => {
		await page.locator(`.results`).click({ force: true });
		await expect(
			page.locator(`.BuilderSettingsMain > .BuilderSettingsMain__section`),
		).not.toHaveAttribute("inert");
		await expect(
			page.locator(`.BuilderSettingsMain > .cmc-warning`),
		).toHaveCount(0);
	});

	test("settings should be disabled for cmc", async ({ page }) => {
		await setInstruction(
			page,
			`
with ui.find('results'):
			ui.Text({"cssClasses": "out", "text": "Hello"})
			`,
		);
		await execute(page);
		await page
			.locator(`.results .wf-type-text.component.out`)
			.click({ force: true });
		await expect(
			page.locator(`.BuilderSettingsMain > .BuilderSettingsMain__section`),
		).toHaveAttribute("inert");
		await expect(
			page.locator(`.BuilderSettingsMain > .cmc-warning`),
		).toHaveCount(1);
	});

	test("create nested components", async ({ page }) => {
		await setInstruction(
			page,
			`
with ui.find('results'):
	with ui.ColumnContainer({"cssClasses": "level1"}):
		with ui.Column({"cssClasses": "level2"}):
			ui.Text({"cssClasses": "level3", "text": "Hello"})
			`,
		);
		await execute(page);
		await expect(
			page.locator(
				`.results .wf-type-columns.level1 .wf-type-column.level2 .wf-type-text.level3`,
			),
		).toHaveCount(1);
		await expect(
			page.locator(
				`.results .wf-type-columns.level1 .wf-type-column.level2 .wf-type-text.level3`,
			),
		).toHaveText("Hello");
	});

	test("binding state", async ({ page }) => {
		await setInstruction(
			page,
			`
with ui.find('results'):
	ui.TextInput({"cssClasses": "in"}, binding={"wf-change": "value"})
	ui.Text({"cssClasses": "out", "text": "@{value}"})
			`,
		);
		await execute(page);
		await page.locator(`.results .in input`).fill("Hello");
		await expect(page.locator(`.results .out`)).toHaveText("Hello");
	});

	test("visibility", async ({ page }) => {
		await setInstruction(
			page,
			`
with ui.find('results'):
	ui.Text({"cssClasses": "out", "text": "Hello"}, visible="no")
			`,
		);
		await execute(page);
		await expect(page.locator(`.results .out`)).toBeHidden();
	});

	test("handlers", async ({ page }) => {
		await setInstruction(
			page,
			`
with ui.find('results'):
	ui.TextInput({"cssClasses": "in"}, handlers={"wf-change": update_value})
	ui.Text({"cssClasses": "out", "text": "@{value}"})
			`,
		);
		await execute(page);
		await page.locator(`.results .in input`).fill("Hello");
		await expect(page.locator(`.results .out`)).toHaveText("Hello");
	});
});
