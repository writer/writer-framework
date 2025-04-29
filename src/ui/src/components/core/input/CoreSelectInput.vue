<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreSelectInput"
	>
		<WdsSelect
			v-model="model"
			:options="options"
			:placeholder="fields.placeholder.value"
			hide-icons
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { computed, inject } from "vue";
import { ref } from "vue";
import { FieldType } from "@/writerTypes";
import {
	accentColor,
	containerBackgroundColor,
	cssClasses,
	primaryTextColor,
	separatorColor,
} from "@/renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";
import { validatorObjectRecordNotNested } from "@/constants/validators";
import { validatorPositiveNumber } from "@/constants/validators";

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
				validator: validatorObjectRecordNotNested,
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
				validator: validatorPositiveNumber,
			},
			accentColor,
			primaryTextColor,
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
import WdsSelect, { Option } from "@/wds/WdsSelect.vue";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);

const options = computed(() =>
	Object.entries(fields.options.value).map<Option>(([key, value]) => ({
		value: key,
		label: String(value),
	})),
);

const model = computed<string[]>({
	get() {
		return formValue.value;
	},
	set(value) {
		handleInput(value, "wf-option-change");
	},
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreSelectInput {
	width: fit-content;
	max-width: 70ch;
	width: 100%;
	position: relative;
}

/* Override WDS components from component's styles */

:deep(.WdsSelect__trigger) {
	border-color: var(--separatorColor);
	background-color: var(--containerBackgroundColor);
}
:deep(.WdsSelect__trigger):focus {
	border: 1px solid var(--separatorColor);
}
</style>
