<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreDateInput"
	>
		<input
			type="date"
			:value="formValue"
			@change="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'wf-date-change',
					)
			"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { cssClasses } from "@/renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to select a date using a date picker interface.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_date" to the new value, provided as a YYYY-MM-DD string.

	state["new_date"] = payload`;

export default {
	writer: {
		name: "Date Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			cssClasses,
		},
		events: {
			"wf-date-change": {
				desc: "Capture changes to this control.",
				stub: onChangeHandlerStub,
				bindable: true,
				eventPayloadExample: new Date().toISOString().split("T")[0],
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

.CoreDateInput {
	width: fit-content;
}

input {
	width: 100%;
	max-width: 20ch;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
	cursor: text;
}

input:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
