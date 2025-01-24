import { FieldType, WriterComponentDefinition } from "@/writerTypes";
import {
	cssClasses,
	separatorColor,
	primaryTextColor,
	containerBackgroundColor,
} from "@/renderer/sharedStyleFields";

const description = "A component to embed PDF documents.";

const definition: WriterComponentDefinition = {
	name: "PDF",
	description,
	category: "Embed",
	fields: {
		source: {
			name: "PDF source",
			type: FieldType.Text,
			desc: "A valid URL. Alternatively, you can provide a state reference to a packed PDF file.",
		},
		highlights: {
			name: "Highlights",
			default: JSON.stringify([]),
			desc: "A list of highlights to be applied to the PDF as a JSON array of strings.",
			type: FieldType.Object,
		},
		selectedMatch: {
			name: "Selected highlight match",
			default: null,
			desc: "The index of the selected highlight match.",
			type: FieldType.Number,
		},
		page: {
			name: "Page",
			type: FieldType.Number,
			desc: "The page to be displayed.",
		},
		controls: {
			name: "Controls",
			type: FieldType.Text,
			options: {
				yes: "Yes",
				no: "No",
			},
			desc: "Show controls to navigate the PDF.",
			default: "yes",
		},
		containerBackgroundColor,
		separatorColor,
		primaryTextColor,
		cssClasses,
	},
};

export default definition;
