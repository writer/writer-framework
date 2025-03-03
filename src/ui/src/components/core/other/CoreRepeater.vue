<script lang="ts">
import { computed, h, inject } from "vue";
import { FieldType } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { validatorRepeaterObject } from "@/constants/validators";

const description =
	"A container component that repeats its child components based on a dictionary.";

const defaultRepeaterObject = {
	a: { desc: "Option A" },
	b: { desc: "Option B" },
};

export default {
	writer: {
		name: "Repeater",
		description,
		category: "Other",
		allowedChildrenTypes: ["inherit"],
		fields: {
			repeaterObject: {
				name: "Repeater object",
				default: JSON.stringify(defaultRepeaterObject, null, 2),
				type: FieldType.Object,
				desc: "Include a state reference to the dictionary used for repeating the child components. Alternatively, specify a JSON object.",
				validator: validatorRepeaterObject,
			},
			keyVariable: {
				name: "Key variable name",
				default: "itemId",
				init: "itemId",
				type: FieldType.Text,
				desc: "Set the name of the variable that will store the key of the current repeater object entry.",
			},
			valueVariable: {
				name: "Value variable name",
				default: "item",
				init: "item",
				type: FieldType.Text,
				desc: "Set the name of the variable that will store the value of the current repeater object entry.",
			},
		},
	},
	setup(_, { slots }) {
		const wf = inject(injectionKeys.core);
		const componentId = inject(injectionKeys.componentId);
		const fields = inject(injectionKeys.evaluatedFields);
		const isBeingEdited = inject(injectionKeys.isBeingEdited);
		const renderProxiedComponent = inject(
			injectionKeys.renderProxiedComponent,
		);

		const children = computed(() =>
			wf.getComponents(componentId, { sortedByPosition: true }),
		);
		const getRepeatedChildrenVNodes = () => {
			if (typeof fields.repeaterObject.value !== "object") {
				return [];
			}

			const repeatedChildrenVNodes = Object.values(
				fields.repeaterObject.value,
			).map((_item, itemIndex) =>
				children.value.map((childComponent) =>
					renderProxiedComponent(childComponent.id, itemIndex),
				),
			);
			return repeatedChildrenVNodes;
		};

		return () => {
			let repeater_children = {};
			if (
				children.value.length != 0 &&
				fields.repeaterObject.value != null &&
				Object.keys(fields.repeaterObject.value).length != 0
			) {
				repeater_children = getRepeatedChildrenVNodes();
			} else if (isBeingEdited.value === true) {
				repeater_children = slots.default({});
			} else {
				repeater_children = {};
			}

			return h(
				"div",
				{
					class: "CoreRepeater",
					"data-writer-container": "",
				},
				repeater_children,
			);
		};
	},
};
</script>
<style scoped>
.CoreRepeater:not(.childless) {
	display: contents;
}

[data-writer-container].horizontal .CoreRepeater.childless {
	flex: 1 0 auto;
}
</style>
