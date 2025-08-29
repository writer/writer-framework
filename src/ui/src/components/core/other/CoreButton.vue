<template>
	<WdsButton
		ref="rootInstance"
		class="CoreButton"
		:aria-disabled="isDisabled"
		:disabled="!isBeingEdited && isDisabled"
		@click="handleClick"
	>
		<WdsIcon
			v-if="fields.lucideIcon.value"
			:name="fields.lucideIcon.value"
		/>
		<span class="CoreButton__text">{{ fields.text.value }}</span>
	</WdsButton>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import WdsButton from "@/wds/WdsButton.vue";
import {
	buttonColor,
	buttonTextColor,
	buttonShadow,
	separatorColor,
	cssClasses,
	createBooleanField,
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
			lucideIcon: {
				name: "Icon",
				type: FieldType.Text,
				desc: 'Lucide icon name in kebab-case, e.g. "badge-check".',
			},
			isDisabled: createBooleanField({
				name: "Disabled",
				default: "no",
				desc: "Disables all event handlers.",
			}),
			buttonColor,
			buttonTextColor,
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
import WdsIcon from "@/wds/WdsIcon.vue";

const rootInstance = ref<ComponentPublicInstance | null>(null);
const fields = inject(injectionKeys.evaluatedFields);
const isDisabled = inject(injectionKeys.isDisabled);
const isBeingEdited = inject(injectionKeys.isBeingEdited);

watch(
	fields.isDisabled,
	(newFieldValue: boolean) => {
		isDisabled.value = newFieldValue;
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

.CoreButton.selected {
	color: var(--wdsColorBlue5);
	opacity: 1;
}

.CoreButton__text {
	overflow: hidden;
	text-overflow: ellipsis;
}
</style>
