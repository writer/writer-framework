<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreNumberInput"
	>
		<input
			ref="inputEl"
			type="number"
			:value="formValue"
			:placeholder="fields.placeholder.value"
			:min="
				fields.minValue.value !== null
					? fields.minValue.value
					: undefined
			"
			:max="
				fields.maxValue.value !== null
					? fields.maxValue.value
					: undefined
			"
			:step="
				fields.valueStep.value !== null
					? fields.valueStep.value
					: undefined
			"
			@input="handleInputEvent"
			@change="handleChangeEvent"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { cssClasses } from "@/renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to enter numeric values.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	writer: {
		name: "Number Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			placeholder: {
				name: "Placeholder",
				type: FieldType.Text,
			},
			minValue: {
				name: "Minimum value",
				type: FieldType.Number,
				default: null,
			},
			maxValue: {
				name: "Max value",
				type: FieldType.Number,
				default: null,
			},
			valueStep: {
				name: "Step",
				type: FieldType.Number,
				default: "1",
			},
			cssClasses,
		},
		events: {
			"wf-number-change": {
				desc: "Capture changes as they happen.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
			"wf-number-change-finish": {
				desc: "Capture changes once this control has lost focus.",
				stub: onChangeHandlerStub,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = useTemplateRef("rootInstance");
const inputEl = useTemplateRef("inputEl");
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);

function enforceLimitsAndReturnValue() {
	if (inputEl.value.value == "") return null;

	let v: number = parseFloat(inputEl.value.value);

	if (isNaN(v)) return v;
	if (fields.minValue.value !== null && v < fields.minValue.value) {
		v = fields.minValue.value;
		inputEl.value.value = v;
	}
	if (fields.maxValue.value !== null && v > fields.maxValue.value) {
		v = fields.maxValue.value;
		inputEl.value.value = v;
	}
	return v;
}

function handleInputEvent() {
	const v = enforceLimitsAndReturnValue();
	if (isNaN(v)) return;
	handleInput(v, "wf-number-change");
}

function handleChangeEvent() {
	const v = enforceLimitsAndReturnValue();
	if (isNaN(v)) return;
	handleInput(v, "wf-number-change-finish");
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreNumberInput {
	max-width: 70ch;
	width: 100%;
}

input {
	max-width: 30ch;
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
}

input:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
