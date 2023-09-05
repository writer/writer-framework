<template>
	<div class="CoreSelectInput" ref="rootEl">
		<div class="labelContainer" v-if="fields.label.value || fields.label.value === 0">
			<label>{{ fields.label.value }}</label>
		</div>
		<BaseSelect :options="options" :maximum-count="1" mode="single"></BaseSelect>
	</div>
</template>

<script lang="ts">
import { computed, inject, Ref } from "vue";
import { ref } from "vue";
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description =
	"A user input component that allows users to select a single value from a list of options using a dropdown menu.";
const defaultOptions = { a: "Option A", b: "Option B" };
const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected option

	state["selected"] = payload`;

export default {
	streamsync: {
		name: "Multiselect Input",
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
			maximumCount: {
				name: "Maximum count",
				desc: "The maximum allowable number of selected options. Set to zero for unlimited.",
				type: FieldType.Number,
				default: "0"
			},
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
import BaseSelect from "../base/BaseSelect.vue";

const fields = inject(injectionKeys.evaluatedFields);
const options = computed(() => fields.options.value);
const maximumCount:Ref<number> = computed(() => fields.maximumCount.value);
const rootEl: Ref<HTMLElement> = ref(null);
const ss = inject(injectionKeys.core);
const componentId = inject(injectionKeys.componentId);

const { formValue, handleInput } = useFormValueBroker(ss, componentId, rootEl);

</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.CoreSelectInput {
	width: fit-content;
	max-width: 100%;
	width: 100%;
	position: relative;
}

.labelContainer {
	margin-bottom: 8px;
	color: var(--primaryTextColor);
}

</style>
