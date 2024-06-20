<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreDropdownInput"
	>
		<WdsDropdownInput
			v-model="formValue"
			@input="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'wf-option-change',
					)
			"
		>
			<option
				v-for="(option, optionKey) in fields.options.value"
				:key="optionKey"
				:value="optionKey"
			>
				{{ option }}
			</option>
		</WdsDropdownInput>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { inject } from "vue";
import { ref } from "vue";
import { FieldType } from "../../writerTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import WdsDropdownInput from "../../wds/WdsDropdownInput.vue";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to select a single value from a list of options using a dropdown menu.";
const defaultOptions = { a: "Option A", b: "Option B" };
const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected option

	state["selected"] = payload`;

export default {
	writer: {
		name: "Dropdown Input",
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
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";

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
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

.CoreDropdownInput {
	width: fit-content;
	max-width: 100%;
}
</style>
