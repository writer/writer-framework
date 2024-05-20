<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreSliderInput"
	>
		<div class="inputArea">
			<input
				type="range"
				:value="formValue"
				:min="fields.minValue.value"
				:max="fields.maxValue.value"
				:step="fields.stepSize.value"
				@input="
					($event) =>
						handleInput(
							($event.target as HTMLInputElement).value,
							'wf-number-change',
						)
				"
			/>
			<div class="valueContainer">
				<h3>{{ formValue }}</h3>
			</div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { FieldType } from "../../writerTypes";
import { accentColor, cssClasses } from "../../renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";

const description =
	"A user input component that allows users to select numeric values using a slider with optional constraints like min, max, and step.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	writer: {
		name: "Slider Input",
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
			cssClasses,
		},
		events: {
			"wf-number-change": {
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

.CoreSliderInput {
	width: 100%;
	max-width: 50ch;
}

.inputArea {
	display: flex;
	align-items: center;
	gap: 8px;
	border-radius: 8px;
	border: 1px solid transparent;
}

input {
	flex: 1 1 auto;
	min-width: 0;
	margin: 0;
	accent-color: var(--accentColor);
	border-radius: 8px;
	height: 38px;
	outline: none;
}

.valueContainer {
	min-width: 0;
	flex: 0 0 auto;
	text-align: center;
}
</style>
