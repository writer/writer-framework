<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreTextareaInput"
	>
		<textarea
			:value="formValue"
			:placeholder="fields.placeholder.value"
			:rows="fields.rows.value"
			@input="
				($event) =>
					handleInput(
						($event.target as HTMLTextAreaElement).value,
						'wf-change',
					)
			"
			@change="
				($event) =>
					handleInput(
						($event.target as HTMLTextAreaElement).value,
						'wf-change-finish',
					)
			"
		></textarea>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldControl, FieldType } from "@/writerTypes";
import { cssClasses } from "@/renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to enter multi-line text values.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	writer: {
		name: "Textarea Input",
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
				control: FieldControl.Textarea,
			},
			rows: {
				name: "Rows",
				type: FieldType.Number,
				init: "5",
				default: "5",
			},
			cssClasses,
		},
		events: {
			"wf-change": {
				desc: "Capture changes as they happen.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
			"wf-change-finish": {
				desc: "Capture changes once this control has lost focus.",
				stub: onChangeHandlerStub,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreTextareaInput {
	max-width: 70ch;
	width: 100%;
}

label {
	display: block;
	margin-bottom: 8px;
	color: var(--primaryTextColor);
}

textarea {
	resize: vertical;
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
}

textarea:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
