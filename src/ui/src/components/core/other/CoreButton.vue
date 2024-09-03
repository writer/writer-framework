<docs lang="md">
    Writer Framework uses Material Symbols to display icons. To include an icon, check https://fonts.google.com/icons, find the icon's id (such as \`arrow_forward\`) and it to your _Button_.
</docs>

<template>
	<WdsButton
		ref="rootInstance"
		class="CoreButton"
		:aria-disabled="isDisabled"
		@click="handleClick"
	>
		<i v-if="fields.icon.value" class="material-symbols-outlined">{{
			fields.icon.value
		}}</i>
		{{ fields.text.value }}
	</WdsButton>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import WdsButton from "@/wds/WdsButton.vue";
import {
	buttonColor,
	buttonTextColor,
	buttonShadow,
	separatorColor,
	cssClasses,
} from "@/renderer/sharedStyleFields";
import { watch } from "vue";
import { getClick } from "@/renderer/syntheticEvents";

const clickHandlerStub = `
def handle_button_click(state):

	# Increment counter when the button is clicked

	state["counter"] += 1`;

const description =
	"A standalone button component that can be linked to a click event handler.";

export default {
	writer: {
		name: "Button",
		description,
		category: "Other",
		events: {
			"wf-click": {
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
				desc: "Disables all event handlers.",
			},
			buttonColor,
			buttonTextColor,
			icon: {
				name: "Icon",
				type: FieldType.Text,
				desc: `A Material Symbols id, such as "arrow_forward".`,
				category: FieldCategory.Style,
			},
			buttonShadow,
			separatorColor,
			cssClasses,
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { ComponentPublicInstance, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";

const rootInstance = ref<ComponentPublicInstance | null>(null);
const fields = inject(injectionKeys.evaluatedFields);
const isDisabled = inject(injectionKeys.isDisabled);

watch(
	fields.isDisabled,
	(newFieldValue: string) => {
		isDisabled.value = newFieldValue == "yes";
	},
	{
		immediate: true,
	},
);

function handleClick(ev: MouseEvent) {
	if (!rootInstance.value) return;
	const ssEv = getClick(ev);
	rootInstance.value.$el.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreButton.disabled {
	border: 1px solid var(--separatorColor);
	cursor: default;
	opacity: 0.4;
	filter: contrast(90%);
}
</style>
