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
			:enable-multi-selection="fields.allowMultiSelect.value"
			hide-icons
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { computed, inject } from "vue";
import { ref } from "vue";
import {
	FieldCategory,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";
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
import { WdsColor } from "@/wds/tokens";

const description =
	"A user input component that allows users to select a single or multiples value(s) from a searchable list of options.";
const defaultOptions = { a: "Option A", b: "Option B" };
const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected option

	state["selected"] = payload`;

export default {
	writer: {
		name: "Select input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			allowMultiSelect: {
				name: "Allow Multi-select",
				desc: "Select more than one option from the dropdown.",
				type: FieldType.Boolean,
			},
			options: {
				name: "Options",
				desc: "Key-value object with options. Must be a JSON string or a state reference to a dictionary.",
				type: FieldType.KeyValue,
				default: JSON.stringify(defaultOptions, null, 2),
				validator: validatorObjectRecordNotNested,
			},
			defaultValue: {
				name: "Default value",
				desc: "Default selected option(s). For single-select, provide a single value key. For multi-select, provide comma-separated value keys (e.g., 'a, b, c').",
				type: FieldType.Text,
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
				enabled(context) {
					const fields = context.evaluatedFields;
					return Boolean(fields.allowMultiSelect.value);
				},
			},
			accentColor,
			primaryTextColor,
			chipTextColor: {
				name: "Chip text",
				type: FieldType.Color,
				default: WdsColor.White,
				desc: "The colour of the text in the chips.",
				category: FieldCategory.Style,
				applyStyleVariable: true,
				enabled(context) {
					const fields = context.evaluatedFields;
					return Boolean(fields.allowMultiSelect.value);
				},
			},
			containerBackgroundColor,
			separatorColor,
			cssClasses,
		},
		events: {
			"wf-option-change": {
				desc: "Sent when the selected option changes.",
				stub: onChangeHandlerStub.trim(),
				bindable: true,
				enabled(context) {
					const fields = context.evaluatedFields;
					return !fields.allowMultiSelect.value;
				},
			},
			"wf-options-change": {
				desc: "Sent when the selected options change.",
				stub: onChangeHandlerStub.trim(),
				bindable: true,
				eventPayloadExample: Object.keys(defaultOptions),
				enabled(context) {
					const fields = context.evaluatedFields;
					return Boolean(fields.allowMultiSelect.value);
				},
			},
		},
	} satisfies WriterComponentDefinition,
};
</script>

<script setup lang="ts">
import { watch } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";
import WdsSelect, { Option } from "@/wds/WdsSelect.vue";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const defaultValue = computed(() => {
	const value = fields.defaultValue.value?.trim();
	if (!value) return [];

	if (fields.allowMultiSelect.value) {
		return value
			.split(",")
			.map((item) => item.trim())
			.filter((item) => Object.keys(fields.options.value).includes(item));
	} else {
		if (!Object.keys(fields.options.value).includes(value)) {
			return "";
		}
		return value;
	}
});

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
	defaultValue.value,
);

watch(fields.allowMultiSelect, () => {
	formValue.value = defaultValue.value;
});

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
		const event = fields.allowMultiSelect.value
			? "wf-options-change"
			: "wf-option-change";
		handleInput(value, event);
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
