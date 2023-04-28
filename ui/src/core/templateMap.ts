// Maps Streamsync component types to renderable Vue components

import CorePage from "../core_components/CorePage.vue";
import CoreSidebar from "../core_components/CoreSidebar.vue";
import CoreText from "../core_components/CoreText.vue";
import CoreButton from "../core_components/CoreButton.vue";
import CoreSection from "../core_components/CoreSection.vue";
import CoreHeader from "../core_components/CoreHeader.vue";
import CoreHeading from "../core_components/CoreHeading.vue";
import CoreDataframe from "../core_components/CoreDataframe.vue";
import CoreHtml from "../core_components/CoreHtml.vue";
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
import CoreCheckboxInput from "../core_components/input/CoreCheckboxInput.vue";
import CoreFileInput from "../core_components/input/CoreFileInput.vue";
import CoreMetric from "../core_components/CoreMetric.vue";
import CoreMessage from "../core_components/CoreMessage.vue";
import CoreVideoPlayer from "../core_components/CoreVideoPlayer.vue";

import { StreamsyncComponentDefinition } from "../streamsyncTypes";

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
	repeater: CoreRepeater,
	column: CoreColumn,
	columns: CoreColumns,
	tab: CoreTab,
	tabs: CoreTabs,
	horizontalstack: CoreHorizontalStack,
	separator: CoreSeparator,
	image: CoreImage,
	timer: CoreTimer,
	textinput: CoreTextInput,
	textareainput: CoreTextareaInput,
	numberinput: CoreNumberInput,
	sliderinput: CoreSliderInput,
	dateinput: CoreDateInput,
	radioinput: CoreRadioInput,
	checkboxinput: CoreCheckboxInput,
	dropdowninput: CoreDropdownInput,
	fileinput: CoreFileInput,
	webcamcapture: CoreWebcamCapture,
	vegalitechart: CoreVegaLiteChart,
	plotlygraph: CorePlotlyGraph,
	metric: CoreMetric,
	message: CoreMessage,
	videoplayer: CoreVideoPlayer,
};

export function getComponentDefinition(
	type: string
): StreamsyncComponentDefinition {
	return templateMap[type]?.streamsync;
}

export function getSupportedComponentTypes() {
	return Object.keys(templateMap);
}

export default templateMap;
