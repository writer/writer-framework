// Maps Streamsync component types to renderable Vue components

import CorePage from "../core_components/CorePage.vue";
import CoreSidebar from "../core_components/CoreSidebar.vue";
import CoreText from "../core_components/CoreText.vue";
import CoreButton from "../core_components/CoreButton.vue";
import CoreIcon from "../core_components/CoreIcon.vue";
import CoreSection from "../core_components/CoreSection.vue";
import CoreHeader from "../core_components/CoreHeader.vue";
import CoreHeading from "../core_components/CoreHeading.vue";
import CoreDataframe from "../core_components/CoreDataframe.vue";
import CoreHtml from "../core_components/CoreHtml.vue";
import CorePagination from "../core_components/CorePagination.vue";
import CoreRepeater from "../core_components/CoreRepeater.vue";
import CoreColumn from "../core_components/CoreColumn.vue";
import CoreColumns from "../core_components/CoreColumns.vue";
import CoreHorizontalStack from "../core_components/CoreHorizontalStack.vue";
import CoreSeparator from "../core_components/CoreSeparator.vue";
import CoreTab from "../core_components/CoreTab.vue";
import CoreTabs from "../core_components/CoreTabs.vue";
import CoreImage from "../core_components/CoreImage.vue";
import CoreTimer from "../core_components/CoreTimer.vue";
import CoreWebcamCapture from "../core_components/CoreWebcamCapture.vue";
import CoreVegaLiteChart from "../core_components/CoreVegaLiteChart.vue";
import CorePlotlyGraph from "../core_components/CorePlotlyGraph.vue";
import CoreRoot from "../core_components/CoreRoot.vue";
import CoreTextInput from "../core_components/input/CoreTextInput.vue";
import CoreTextareaInput from "../core_components/input/CoreTextareaInput.vue";
import CoreNumberInput from "../core_components/input/CoreNumberInput.vue";
import CoreSliderInput from "../core_components/input/CoreSliderInput.vue";
import CoreDateInput from "../core_components/input/CoreDateInput.vue";
import CoreRadioInput from "../core_components/input/CoreRadioInput.vue";
import CoreDropdownInput from "../core_components/input/CoreDropdownInput.vue";
import CoreSelectInput from "../core_components/input/CoreSelectInput.vue";
import CoreMultiselectInput from "../core_components/input/CoreMultiselectInput.vue";
import CoreCheckboxInput from "../core_components/input/CoreCheckboxInput.vue";
import CoreFileInput from "../core_components/input/CoreFileInput.vue";
import CoreMetric from "../core_components/CoreMetric.vue";
import CoreMessage from "../core_components/CoreMessage.vue";
import CoreVideoPlayer from "../core_components/CoreVideoPlayer.vue";

import { StreamsyncComponentDefinition } from "../streamsyncTypes";
import { h } from "vue";



const templateMap = {
	root: CoreRoot,
	page: CorePage,
	sidebar: CoreSidebar,
	button: CoreButton,
	text: CoreText,
	section: CoreSection,
	header: CoreHeader,
	heading: CoreHeading,
	dataframe: CoreDataframe,
	html: CoreHtml,
	pagination: CorePagination,
	repeater: CoreRepeater,
	column: CoreColumn,
	columns: CoreColumns,
	tab: CoreTab,
	tabs: CoreTabs,
	horizontalstack: CoreHorizontalStack,
	separator: CoreSeparator,
	image: CoreImage,
	icon: CoreIcon,
	timer: CoreTimer,
	textinput: CoreTextInput,
	textareainput: CoreTextareaInput,
	numberinput: CoreNumberInput,
	sliderinput: CoreSliderInput,
	dateinput: CoreDateInput,
	radioinput: CoreRadioInput,
	checkboxinput: CoreCheckboxInput,
	dropdowninput: CoreDropdownInput,
	selectinput: CoreSelectInput,
	multiselectinput: CoreMultiselectInput,
	fileinput: CoreFileInput,
	webcamcapture: CoreWebcamCapture,
	vegalitechart: CoreVegaLiteChart,
	plotlygraph: CorePlotlyGraph,
	metric: CoreMetric,
	message: CoreMessage,
	videoplayer: CoreVideoPlayer,
};

if (STREAMSYNC_LIVE_CCT === "yes") {

	/*
	Assigns the components in custom_components to the template map,
	allowing for live updates when developing custom component templates. 
	*/

	const liveCCT:Record<string, any> = (await import("../custom_components")).default;
	Object.entries(liveCCT).forEach(([componentType, template]) => {
		templateMap[`custom_${componentType}`] = template;
	});
}


function fallbackTemplate(type: string) {
	const message = `Component type "${type}" not supported. If it's a custom component, please ensure it's been loaded.`;
	return {
		streamsync: {
			name: "Fallback Component",
			allowedChildrenTypes: ["*"],
			description: message,
			category: "Fallback",
		},
		setup(props, { slots }) {
			return () => {
				return h(
					"div",
					{
						"data-streamsync-container": "",
						style: {
							color: "var(--primaryTextColor)",
						},
					},
					[message, slots.default({})],
				);
			};
		},
	};
}

export function getTemplate(type: string) {
	return templateMap[type] ?? fallbackTemplate(type);
}

export function getComponentDefinition(
	type: string,
): StreamsyncComponentDefinition {
	return getTemplate(type)?.streamsync;
}

export function getSupportedComponentTypes() {
	return Object.keys(templateMap);
}

export function registerComponentTemplate(type: string, vueComponent: any) {
	templateMap[type] = vueComponent;
}

export default templateMap;
