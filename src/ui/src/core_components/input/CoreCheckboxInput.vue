<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreCheckboxInput"
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
					type="checkbox"
					:checked="
						Array.isArray(formValue)
							? formValue.includes(optionKey)
							: false
					"
					:value="optionKey"
					@input="
						($event) =>
							handleInput(getCheckedKeys(), 'ss-options-change')
					"
				/><label :for="`${flattenedInstancePath}-option-${optionKey}`">
					{{ option }}
				</label>
			</div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { ComponentPublicInstance, inject } from "vue";
import { ref } from "vue";
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	cssClasses,
	primaryTextColor,
} from "../../renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const defaultOptions = { a: "Option A", b: "Option B" };

const description =
	"A user input component that allows users to choose multiple values from a list of options using checkboxes.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected options.
	# The payload will be a list, as multiple options are allowed.

	state["selected"] = payload`;

export default {
	streamsync: {
		name: "Checkbox Input",
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
			"ss-options-change": {
				desc: "Sent when the selected options change.",
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
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const flattenedInstancePath = inject(injectionKeys.flattenedInstancePath);

const { formValue, handleInput } = useFormValueBroker(
	ss,
	instancePath,
	rootInstance,
);

function getCheckedKeys() {
	if (!rootInstance.value) return;
	const checkboxEls = Array.from(
		rootInstance.value.$el.querySelectorAll(`input[type="checkbox"]`),
	) as HTMLInputElement[];
	const checkedValues = checkboxEls
		.map((checkboxEl) =>
			checkboxEl.checked ? checkboxEl.value : undefined,
		)
		.filter((el) => typeof el != "undefined");
	return checkedValues;
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

.CoreCheckboxInput {
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
	margin-right: 8px;
	accent-color: var(--accentColor);
	outline-color: var(--softenedAccentColor);
}
</style>
