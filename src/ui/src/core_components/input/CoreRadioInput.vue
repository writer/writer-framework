<template>
	<BaseInputWrapper
		ref="rootEl"
		:label="fields.label.value"
		class="CoreRadioInput"
	>
		<div
			class="options"
			:class="{
				horizontal: fields.orientation.value == 'horizontal',
			}"
		>
			<div
				v-for="(option, optionKey) in fields.options.value"
				:key="optionKey"
				class="option"
			>
				<input
					:id="`${flattenedInstancePath}-option-${optionKey}`"
					type="radio"
					:checked="formValue === optionKey"
					:value="optionKey"
					:name="`${flattenedInstancePath}-options`"
					@input="
						($event) => handleInput(optionKey, 'ss-option-change')
					"
				/><label
					:for="`${flattenedInstancePath}-option-${optionKey}`"
					>{{ option }}</label
				>
			</div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { inject, Ref } from "vue";
import { ref } from "vue";
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	cssClasses,
	primaryTextColor,
} from "../../renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const description =
	"A user input component that allows users to choose a single value from a list of options using radio buttons.";

const defaultOptions = { a: "Option A", b: "Option B" };

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected radio option

	state["selected"] = payload`;

export default {
	streamsync: {
		name: "Radio Input",
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
			orientation: {
				name: "Orientation",
				type: FieldType.Text,
				options: {
					vertical: "Vertical",
					horizontal: "Horizontal",
				},
				default: "vertical",
				category: FieldCategory.Style,
				desc: "Specify how to lay out the options.",
			},
			primaryTextColor,
			accentColor,
			cssClasses,
		},
		events: {
			"ss-option-change": {
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
const flattenedInstancePath = inject(injectionKeys.flattenedInstancePath);
const rootEl: Ref<HTMLElement> = ref(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.CoreRadioInput {
	width: fit-content;
	max-width: 100%;
}

.options {
	display: flex;
	flex-direction: column;
	gap: 5px;
}

.options.horizontal {
	flex-direction: row;
	flex-wrap: wrap;
}

.option {
	display: flex;
	align-items: center;
	color: var(--primaryTextColor);
	font-size: 0.75rem;
}

input {
	margin: 0 8px 0 0;
	accent-color: var(--accentColor);
}
</style>
