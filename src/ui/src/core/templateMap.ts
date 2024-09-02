// Maps Writer Framework component types to renderable Vue components
// content
import CoreDataframe from "../components/core/content/CoreDataframe.vue";
import CoreHeading from "../components/core/content/CoreHeading.vue";
import CoreIcon from "../components/core/content/CoreIcon.vue";
import CoreImage from "../components/core/content/CoreImage.vue";
import CoreMessage from "../components/core/content/CoreMessage.vue";
import CoreMetric from "../components/core/content/CoreMetric.vue";
import CorePlotlyGraph from "../components/core/content/CorePlotlyGraph.vue";
import CoreText from "../components/core/content/CoreText.vue";
import CoreVegaLiteChart from "../components/core/content/CoreVegaLiteChart.vue";
import CoreVideoPlayer from "../components/core/content/CoreVideoPlayer.vue";
import CoreLink from "../components/core/content/CoreLink.vue";
import CoreChatbot from "../components/core/content/CoreChatbot.vue";
import CoreTags from "../components/core/content/CoreTags.vue";
import CoreAvatar from "../components/core/content/CoreAvatar.vue";
import CoreAnnotatedText from "../components/core/content/CoreAnnotatedText.vue";
import CoreJsonViewer from "../components/core/content/CoreJsonViewer.vue";

// input
import CoreCheckboxInput from "../components/core/input/CoreCheckboxInput.vue";
import CoreColorInput from "../components/core/input/CoreColorInput.vue";
import CoreDateInput from "../components/core/input/CoreDateInput.vue";
import CoreDropdownInput from "../components/core/input/CoreDropdownInput.vue";
import CoreFileInput from "../components/core/input/CoreFileInput.vue";
import CoreMultiselectInput from "../components/core/input/CoreMultiselectInput.vue";
import CoreNumberInput from "../components/core/input/CoreNumberInput.vue";
import CoreRadioInput from "../components/core/input/CoreRadioInput.vue";
import CoreSelectInput from "../components/core/input/CoreSelectInput.vue";
import CoreSliderInput from "../components/core/input/CoreSliderInput.vue";
import CoreTextInput from "../components/core/input/CoreTextInput.vue";
import CoreTextareaInput from "../components/core/input/CoreTextareaInput.vue";
import CoreTimeInput from "../components/core/input/CoreTimeInput.vue";
import CoreRating from "../components/core/input/CoreRatingInput.vue";
import CoreSwitchInput from "../components/core/input/CoreSwitchInput.vue";
// layout
import CoreColumn from "../components/core/layout/CoreColumn.vue";
import CoreColumns from "../components/core/layout/CoreColumns.vue";
import CoreHeader from "../components/core/layout/CoreHeader.vue";
import CoreHorizontalStack from "../components/core/layout/CoreHorizontalStack.vue";
import CoreSection from "../components/core/layout/CoreSection.vue";
import CoreSeparator from "../components/core/layout/CoreSeparator.vue";
import CoreSidebar from "../components/core/layout/CoreSidebar.vue";
import CoreTab from "../components/core/layout/CoreTab.vue";
import CoreTabs from "../components/core/layout/CoreTabs.vue";
import CoreStep from "../components/core/layout/CoreStep.vue";
import CoreSteps from "../components/core/layout/CoreSteps.vue";
// other
import CoreButton from "../components/core/other/CoreButton.vue";
import CoreHtml from "../components/core/other/CoreHtml.vue";
import CorePagination from "../components/core/other/CorePagination.vue";
import CoreRepeater from "../components/core/other/CoreRepeater.vue";
import CoreTimer from "../components/core/other/CoreTimer.vue";
import CoreWebcamCapture from "../components/core/other/CoreWebcamCapture.vue";
import CoreReuse from "../components/core/other/CoreReuse.vue";
// embed
import CorePDF from "../components/core/embed/CorePDF.vue";
import CoreIFrame from "../components/core/embed/CoreIFrame.vue";
import CoreGoogleMaps from "../components/core/embed/CoreGoogleMaps.vue";
// root
import CorePage from "../components/core/root/CorePage.vue";
import CoreRoot from "../components/core/root/CoreRoot.vue";
import CoreMapbox from "../components/core/embed/CoreMapbox.vue";

// WORKFLOWS

import WorkflowsWorkflow from "../components/workflows/WorkflowsWorkflow.vue";
import WorkflowsNode from "../components/workflows/abstract/WorkflowsNode.vue";

import { AbstractTemplate, WriterComponentDefinition } from "@/writerTypes";
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
	link: CoreLink,
	horizontalstack: CoreHorizontalStack,
	separator: CoreSeparator,
	image: CoreImage,
	pdf: CorePDF,
	iframe: CoreIFrame,
	googlemaps: CoreGoogleMaps,
	mapbox: CoreMapbox,
	icon: CoreIcon,
	timer: CoreTimer,
	textinput: CoreTextInput,
	textareainput: CoreTextareaInput,
	numberinput: CoreNumberInput,
	sliderinput: CoreSliderInput,
	colorinput: CoreColorInput,
	dateinput: CoreDateInput,
	timeinput: CoreTimeInput,
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
	chatbot: CoreChatbot,
	step: CoreStep,
	steps: CoreSteps,
	ratinginput: CoreRating,
	tags: CoreTags,
	switchinput: CoreSwitchInput,
	reuse: CoreReuse,
	avatar: CoreAvatar,
	annotatedtext: CoreAnnotatedText,
	jsonviewer: CoreJsonViewer,
	workflow: WorkflowsWorkflow,
	workflowsnode: WorkflowsNode,
};

const abstractTemplateMap: Record<string, AbstractTemplate> = {};

if (WRITER_LIVE_CCT === "yes") {
	/*
	Assigns the components in custom_components to the template map,
	allowing for live updates when developing custom component templates.
	*/

	const liveCCT: Record<string, any> = (await import("../custom_components"))
		.default;
	Object.entries(liveCCT).forEach(([componentType, template]) => {
		templateMap[`custom_${componentType}`] = template;
	});
}

function fallbackTemplate(type: string) {
	const message = `Component type "${type}" not supported. If it's a custom component, please ensure it's been loaded.`;
	return {
		writer: {
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
						"data-writer-container": "",
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

function getMergedAbstractTemplate(type: string) {
	const template = abstractTemplateMap[type];
	if (!template) return;
	const baseType = template.baseType;
	return {
		...templateMap[baseType],
		writer: {
			...templateMap[baseType].writer,
			...abstractTemplateMap[type].writer,
			fields: {
				...templateMap[baseType].writer?.fields,
				...abstractTemplateMap[type].writer?.fields,
			},
		},
	};
}

export function getTemplate(type: string) {
	return (
		getMergedAbstractTemplate(type) ??
		templateMap[type] ??
		fallbackTemplate(type)
	);
}

export function getComponentDefinition(
	type: string,
): WriterComponentDefinition {
	return getTemplate(type)?.writer;
}

export function getSupportedComponentTypes() {
	return [...Object.keys(templateMap), ...Object.keys(abstractTemplateMap)];
}

export function registerComponentTemplate(type: string, vueComponent: any) {
	templateMap[type] = vueComponent;
}

export function registerAbstractComponentTemplate(
	type: string,
	abstractTemplate: AbstractTemplate,
) {
	abstractTemplateMap[type] = abstractTemplate;
}

export default templateMap;
