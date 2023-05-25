<template>
	<div class="CoreRadioInput" ref="rootEl">
		<div class="main">
			<div class="inputContainer">
				<label class="mainLabel">{{ fields.label.value }}</label>
				<div class="options">
					<div
						class="option"
						v-for="(option, optionKey) in fields.options.value"
						:key="optionKey"
					>
						<input
							type="radio"
							:checked="formValue === optionKey"
							v-on:input="
								($event) =>
									handleInput(optionKey, 'ss-option-change')
							"
							:value="optionKey"
							:id="`${flattenedInstancePath}-option-${optionKey}`"
							:name="`${flattenedInstancePath}-options`"
						/><label
							:for="`${flattenedInstancePath}-option-${optionKey}`"
							>{{ option }}</label
						>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { computed, inject, Ref } from "vue";
import { ref } from "vue";
import { FieldType } from "../../streamsyncTypes";

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
				control: "object",
				desc: "Key-value object with options. Must be a JSON string or a state reference to a dictionary.",
				type: FieldType.KeyValue,
				default: JSON.stringify(defaultOptions, null, 2),
			},
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
const instancePath = inject(injectionKeys.instancePath);
const rootEl: Ref<HTMLElement> = ref(null);
const ss = inject(injectionKeys.core);
const componentId = inject(injectionKeys.componentId);

const { formValue, handleInput } = useFormValueBroker(ss, componentId, rootEl);

const flattenedInstancePath = computed(() => {
	const flat = instancePath
		.map((item) => `${item.componentId}:${item.instanceNumber}`)
		.join(".");
	return flat;
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.CoreRadioInput {
	width: 100%;
}

.options {
	display: flex;
	flex-direction: column;
	margin-top: 4px;
}

.option {
	margin-top: 8px;
	display: flex;
	align-items: center;
	color: var(--primaryTextColor);
	font-size: 0.75rem;
}

input {
	margin: 0 8px 0 0;
}

label {
	color: var(--primaryTextColor);
}
</style>
