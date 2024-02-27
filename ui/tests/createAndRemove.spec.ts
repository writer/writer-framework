import { test, expect } from "@playwright/test";

test.setTimeout(50000);

const components = [
	{ type: "sidebar", locator: `div.CoreSidebar.component` },
	{ type: "button", locator: `button.CoreButton.component` },
	{ type: "text", locator: `div.CoreText.component` },
	//{ type: "section", locator: `div.CoreSection.component` },
	{ type: "header", locator: `div.CoreHeader.component` },
	{ type: "heading", locator: `div.CoreHeading.component` },
	{ type: "dataframe", locator: `div.CoreDataframe.component` },
	{ type: "html", locator: `div.CoreHTML.component` },
	{ type: "pagination", locator: `div.pagination.component` },
	{ type: "repeater", locator: `div.CoreRepeater.component` },
	//{ type: "column", locator: `div.CoreColumn.component` },
	{ type: "columns", locator: `div.CoreColumns.component` },
	//{ type: "tab", locator: `div.CoreTab.component` },
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
	{ type: "sliderinput", locator: `div.CoreSliderInput.component` },
	{ type: "dateinput", locator: `div.CoreDateInput.component` },
	{ type: "radioinput", locator: `div.CoreRadioInput.component` },
	{ type: "checkboxinput", locator: `div.CoreCheckboxInput.component` },
	{ type: "dropdowninput", locator: `div.CoreDropdownInput.component` },
	{ type: "selectinput", locator: `div.CoreSelectInput.component` },
	{ type: "multiselectinput", locator: `div.CoreMultiselectInput.component` },
	{ type: "fileinput", locator: `div.CoreFileInput.component` },
	{ type: "webcamcapture", locator: `div.CoreWebcamCapture.component` },
	{ type: "vegalitechart", locator: `div.CoreVegaLiteChart.component` },
	{ type: "plotlygraph", locator: `div.CorePlotlyGraph.component` },
	{ type: "metric", locator: `div.CoreMetric.component` },
	{ type: "message", locator: `div.CoreMessage.component` },
	{ type: "videoplayer", locator: `div.CoreVideoPlayer.component` },
];

const loadPreset = async (preset) => {
	await fetch(`http://localhost:7358/${preset}`);
}

components.forEach(({ type, locator }) => {
	test.describe(type, () => {
		const TYPE = type;
		const COMPONENT_LOCATOR = locator;

		test.beforeAll(async() => {
			await loadPreset('base');
		});

		test.beforeEach(async ({ page }) => {
			await page.goto("/");
		});

		test("create", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(".CoreSection .ChildlessPlaceholder"));
		});

		test("remove", async ({ page }) => {
			await page.locator(COMPONENT_LOCATOR).click({timeout: 1000});
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-action="delete"]',
				)
				.click({timeout: 1000});
			await expect(page.locator(COMPONENT_LOCATOR)).not.toBeVisible({timeout: 1000});
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0, {timeout: 1000});
		});
	});
});
