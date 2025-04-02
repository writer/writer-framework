<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreTextInput"
	>
		<input
			:type="fields.passwordMode.value ? 'password' : 'text'"
			:value="formValue"
			:placeholder="fields.placeholder.value"
			aria-autocomplete="none"
			@input="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'wf-change',
					)
			"
			@change="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'wf-change-finish',
					)
			"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	accentColor,
	baseYesNoField,
	cssClasses,
} from "@/renderer/sharedStyleFields";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to enter single-line text values.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	writer: {
		name: "Text Input",
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
			passwordMode: {
				...baseYesNoField,
				name: "Password mode",
				default: "no",
				category: FieldCategory.Style,
			},
			accentColor,
			cssClasses,
		},
		events: {
			"wf-change": {
				desc: "Capture changes as they happen.",
				stub: onChangeHandlerStub,
				bindable: true,
				eventPayloadExample: "The content of the input",
			},
			"wf-change-finish": {
				desc: "Capture changes once this control has lost focus.",
				stub: onChangeHandlerStub,
				eventPayloadExample: "The content of the input",
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

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

.CoreTextInput {
	max-width: 70ch;
	width: 100%;
}

input {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
	color: var(--primaryTextColor);
}

input:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
