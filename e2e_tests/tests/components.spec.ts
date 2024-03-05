import { test, expect } from "@playwright/test";

test.setTimeout(5000);

const createAndRemove = [
	{ type: "sidebar", locator: `div.CoreSidebar.component` },
	{ type: "section", locator: `section.CoreSection.component` },
	{ type: "columns", locator: `div.CoreColumns.component` },
];

const fullCheck = [
	{ type: "button", locator: `button.CoreButton.component` },
	{ type: "text", locator: `div.CoreText.component` },
	{ type: "header", locator: `div.CoreHeader.component` },
	{ type: "heading", locator: `div.CoreHeading.component` },
	{ type: "dataframe", locator: `div.CoreDataframe.component` },
	{ type: "html", locator: `div.CoreHTML.component` },
	{ type: "pagination", locator: `div.CorePagination.component` },
	{ type: "repeater", locator: `div.CoreRepeater.component` },
	// { type: "column", locator: `div.CoreColumn.component` },
	// { type: "tab", locator: `div.CoreTab.component` },
	{ type: "tabs", locator: `div.CoreTabs.component` },
	{ type: "horizontalstack", locator: `div.CoreHorizontalStack.component` },
	{ type: "separator", locator: `div.CoreSeparator.component` },
	{ type: "image", locator: `div.CoreImage.component` },
	{ type: "pdf", locator: `div.CorePDF.component` },
	{ type: "iframe", locator: `div.CoreIFrame.component` },
	{ type: "googlemaps", locator: `div.CoreGoogleMaps.component` },
	{ type: "icon", locator: `div.icon.component` },
	{ type: "timer", locator: `div.CoreTimer.component` },
	{ type: "textinput", locator: `div.CoreTextInput.component` },
	{ type: "textareainput", locator: `div.CoreTextareaInput.component` },
	{ type: "numberinput", locator: `div.CoreNumberInput.component` },
	{ type: "sliderinput", locator: `div.CoreSliderInput.component label` },
	{ type: "dateinput", locator: `div.CoreDateInput.component label` },
	{ type: "radioinput", locator: `div.CoreRadioInput.component` },
	{ type: "checkboxinput", locator: `div.CoreCheckboxInput.component` },
	{ type: "dropdowninput", locator: `div.CoreDropdownInput.component` },
	{ type: "selectinput", locator: `div.CoreSelectInput.component` },
	{ type: "multiselectinput", locator: `div.CoreMultiselectInput.component` },
	{ type: "fileinput", locator: `div.CoreFileInput.component label` },
	{ type: "webcamcapture", locator: `div.CoreWebcamCapture.component` },
	{ type: "vegalitechart", locator: `div.CoreVegaLiteChart.component` },
	{ type: "plotlygraph", locator: `div.CorePlotlyGraph.component` },
	{ type: "metric", locator: `div.CoreMetric.component` },
	{ type: "message", locator: `div.CoreMessage.component` },
	{ type: "videoplayer", locator: `div.CoreVideoPlayer.component` },
	{ type: "chat", locator: `div.CoreChat.component` },
	// { type: "step", locator: `div.CoreStep.component` },
	{ type: "steps", locator: `div.CoreSteps.component` },
	{ type: "ratinginput", locator: `div.CoreRatingInput.component` },
];

createAndRemove.forEach(({ type, locator }) => {
	test.describe(type, () => {
		const TYPE = type;
		const COMPONENT_LOCATOR = locator;
		const TARGET = ".CorePage";

		test.beforeAll(async ({request}) => {
			const response = await request.get(`/preset/empty_page`);
			expect(response.ok()).toBeTruthy();
		});

		test.beforeEach(async ({ page }) => {
			await page.goto("/");
		});

		test("create and remove", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(TARGET));
			await expect(
				page.locator(TARGET + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);

			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});
	});
});

fullCheck.forEach(({ type, locator }) => {
	test.describe(type, () => {
		const TYPE = type;
		const COMPONENT_LOCATOR = locator;
		const COLUMN1 = ".CoreColumns .CoreColumn:nth-child(1 of .CoreColumn)";
		const COLUMN2 = ".CoreColumns .CoreColumn:nth-child(2 of .CoreColumn)";

		test.beforeAll(async ({request}) => {
			const response = await request.get(`/preset/2columns`);
			expect(response.ok()).toBeTruthy();
		});

		test.beforeEach(async ({ page }) => {
			await page.goto("/");
		});

		test("create, drag and drop and remove", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(COLUMN1));
			await expect(
				page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);
			await expect(
				page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
			).toHaveCount(0);

			await page.locator(COMPONENT_LOCATOR).dragTo(page.locator(COLUMN2));
			await expect(
				page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
			).toHaveCount(0);
			await expect(
				page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);

			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).not.toBeVisible();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});
	});
});
