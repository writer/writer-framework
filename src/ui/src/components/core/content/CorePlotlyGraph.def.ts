import { FieldType, WriterComponentDefinition } from "@/writerTypes";
import { cssClasses } from "@/renderer/sharedStyleFields";

const description = "A component that displays Plotly graphs.";

const defaultSpec = {
	data: [
		{
			x: ["a", "b", "c"],
			y: [22, 25, 29],
			type: "bar",
		},
	],
};
const definition: WriterComponentDefinition = {
	name: "Plotly Graph",
	description,
	category: "Content",
	fields: {
		spec: {
			name: "Graph specification",
			default: JSON.stringify(defaultSpec, null, 2),
			desc: "Plotly graph specification. Pass it using state, e.g. @{fig}, or paste a JSON specification.",
			type: FieldType.Object,
		},
		cssClasses,
	},
	events: {
		"plotly-click": {
			desc: "Sends a list with the clicked points.",
		},
		"plotly-selected": {
			desc: "Sends a list with the selected points.",
		},
		"plotly-deselect": {
			desc: "Triggered when points are deselected.",
		},
	},
};

export default definition;
