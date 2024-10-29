<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreSliderInput"
	>
		<BaseInputSliderRange
			popover-display-mode="always"
			:value="formValue || [20, 50]"
			:min="fields.minValue.value"
			:max="fields.maxValue.value"
			:step="fields.stepSize.value"
			@update:value="handleInput($event, 'wf-range-change')"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { ComponentPublicInstance } from "vue";
import { accentColor, cssClasses } from "@/renderer/sharedStyleFields";
import { FieldCategory, FieldType } from "@/writerTypes";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const description =
	"A user input component that allows users to select numeric values range using a range slider with optional constraints like min, max, and step.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variables "from" & "to" to the new range
	state["from"] = payload[0]
	state["to"] = payload[1]`;

export default {
	writer: {
		name: "Slider Range Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			minValue: {
				name: "Minimum value",
				type: FieldType.Number,
				default: "0",
				init: "0",
			},
			maxValue: {
				name: "Maximum value",
				type: FieldType.Number,
				default: "100",
				init: "100",
			},
			stepSize: {
				name: "Step size",
				type: FieldType.Number,
				default: "1",
				init: "1",
			},
			accentColor,
			popoverColor: {
				name: "Popover color",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
				default: "white",
			},
			popoverBackgroundColor: {
				name: "Popover background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
				default: "rgba(0, 0, 0, 1)",
			},
			cssClasses,
		},
		events: {
			"wf-range-change": {
				desc: "Capture changes to this control.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";
import BaseInputSliderRange from "../base/BaseInputSliderRange.vue";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker<[number, number]>(
	wf,
	instancePath,
	rootInstance,
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreSliderInput {
	width: 100%;
	max-width: 50ch;
}
</style>
