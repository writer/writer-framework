<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreTextInput"
	>
		<WdsTextInput
			:type="fields.passwordMode.value == 'yes' ? 'password' : 'text'"
			:value="formValue"
			:placeholder="fields.placeholder.value"
			aria-autocomplete="none"
			@input="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'ss-change',
					)
			"
			@change="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'ss-change-finish',
					)
			"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import { accentColor, cssClasses } from "../../renderer/sharedStyleFields";
import WdsTextInput from "../../wds/WdsTextInput.vue";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to enter single-line text values.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	streamsync: {
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
				name: "Password mode",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
				category: FieldCategory.Style,
			},
			accentColor,
			cssClasses,
		},
		events: {
			"ss-change": {
				desc: "Capture changes as they happen.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
			"ss-change-finish": {
				desc: "Capture changes once this control has lost focus.",
				stub: onChangeHandlerStub,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	ss,
	instancePath,
	rootInstance,
);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

.CoreTextInput {
	max-width: 70ch;
	width: 100%;
}
</style>
