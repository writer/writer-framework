<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreSelectInput"
	>
		<BaseSelect
			:base-id="flattenedInstancePath"
			:active-value="formValue ? [formValue] : []"
			:options="options"
			:maximum-count="1"
			mode="single"
			:placeholder="fields.placeholder.value"
			@change="handleChange"
		></BaseSelect>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { computed, inject } from "vue";
import { ref } from "vue";
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	accentColor,
	containerBackgroundColor,
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";
import { WdsColor } from "@/wds/tokens";

const description =
	"A user input component that allows users to select a single value from a searchable list of options.";
const defaultOptions = { a: "Option A", b: "Option B" };
const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected option

	state["selected"] = payload`;

export default {
	writer: {
		name: "Select Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			options: {
				name: "Options",
				desc: "Key-value object with options. Must be a JSON string or a state reference to a dictionary.",
				type: FieldType.KeyValue,
				default: JSON.stringify(defaultOptions, null, 2),
			},
			placeholder: {
				name: "Placeholder",
				desc: "Text to show when no options are selected.",
				type: FieldType.Text,
			},
			maximumCount: {
				name: "Maximum count",
				desc: "The maximum allowable number of selected options. Set to zero for unlimited.",
				type: FieldType.Number,
				default: "0",
			},
			accentColor,
			chipTextColor: {
				name: "Chip text",
				type: FieldType.Color,
				default: WdsColor.White,
				desc: "The color of the text in the chips.",
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			separatorColor,
			cssClasses,
		},
		events: {
			"wf-option-change": {
				desc: "Sent when the selected option changes.",
				stub: onChangeHandlerStub.trim(),
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";
import BaseSelect from "../base/BaseSelect.vue";

const fields = inject(injectionKeys.evaluatedFields);
const options = computed(() => fields.options.value);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const flattenedInstancePath = inject(injectionKeys.flattenedInstancePath);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);

function handleChange(selectedOptions: string[]) {
	const selectedOption = selectedOptions?.[0] ?? null;
	handleInput(selectedOption, "wf-option-change");
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreSelectInput {
	width: fit-content;
	max-width: 70ch;
	width: 100%;
	position: relative;
}
</style>
