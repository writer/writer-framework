<script lang="ts">
import { h, inject } from "vue";
import { FieldType } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";

const defaultStyle = {
	padding: "16px",
	"min-height": "64px",
	"min-width": "64px",
	"border-radius": "8px",
	background:
		"linear-gradient(90deg, rgba(41,207,0,1) 0%, rgba(145,231,78,1) 100%)",
};

const description =
	"A generic component that creates customisable HTML elements, which can serve as containers for other components.";

const docs = `
You can configure the element type, styles, and attributes to fit your design requirements. You can link them to state for advanced use cases, such as custom animations.

All valid HTML tags are supported, including tags such as \`iframe\`, allowing you to embed external sites.
`;

export default {
	streamsync: {
		name: "HTML Element",
		description,
		docs,
		category: "Other",
		allowedChildrenTypes: ["*"],
		fields: {
			element: {
				name: "Element",
				default: "div",
				type: FieldType.Text,
				desc: "Set the type of HTML element to create, e.g., 'div', 'section', 'span', etc.",
			},
			styles: {
				name: "Styles",
				default: null,
				init: JSON.stringify(defaultStyle, null, 2),
				type: FieldType.Object,
				desc: "Define the CSS styles to apply to the HTML element using a JSON object or a state reference to a dictionary.",
			},
			attrs: {
				name: "Attributes",
				default: null,
				type: FieldType.Object,
				desc: "Set additional HTML attributes for the element using a JSON object or a dictionary via a state reference.",
			},
		},
	},
	setup(props, { slots }) {
		const fields = inject(injectionKeys.evaluatedFields);
		return () => {
			return h(
				fields.element.value,
				{
					...fields.attrs.value,
					"data-streamsync-container": "",
					style: fields.styles.value,
				},
				slots.default({})
			);
		};
	},
};
</script>
