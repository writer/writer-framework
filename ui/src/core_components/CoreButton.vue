<template>
	<button class="CoreButton" :aria-disabled="isDisabled">
		<i
			v-if="fields.icon.value"
			:class="[`ri-${fields.icon.value}-line`, `ri-${fields.icon.value}`]"
		></i>
		{{ fields.text.value }}
	</button>
</template>

<script lang="ts">
import {
	buttonColor,
	buttonTextColor,
	buttonShadow,
	separatorColor,
	cssClasses
} from "../renderer/sharedStyleFields";
import { watch } from "vue";

const clickHandlerStub = `
def handle_button_click(state):

	# Increment counter when the button is clicked

	state["counter"] += 1`;

const description =
	"A standalone button component that can be linked to a click event handler.";

const docs = `
Streamsync uses the library RemixIcon to display icons. To include an icon, check remixicon.com, find the icon's id (such as \`arrow-up\`) and it to your _Button_.
`;

export default {
	streamsync: {
		name: "Button",
		description,
		docs,
		category: "Other",
		events: {
			click: {
				desc: "Capture single clicks.",
				stub: clickHandlerStub.trim(),
			},
		},
		fields: {
			text: {
				name: "Text",
				init: "Button Text",
				type: FieldType.Text,
			},
			isDisabled: {
				name: "Disabled",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
				desc: "Disables all event handlers."
			},
			buttonColor,
			buttonTextColor,
			icon: {
				name: "Icon",
				type: FieldType.Text,
				desc: `A RemixIcon id, such as "arrow-up".`,
				category: FieldCategory.Style,
			},
			buttonShadow,
			separatorColor,
			cssClasses
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import { FieldCategory, FieldType } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);

const isDisabled = inject(injectionKeys.isDisabled);

watch(fields.isDisabled, (newFieldValue: string) => {
	isDisabled.value = newFieldValue == "yes";
}, {
	immediate: true
});

</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreButton {
	width: fit-content;
	max-width: 100%;
	display: flex;
	align-items: center;
	gap: 8px;
}

.CoreButton.disabled {
	border: 1px solid var(--separatorColor);
	cursor: default;
	opacity: 0.9;
	filter: contrast(90%);
}

</style>
