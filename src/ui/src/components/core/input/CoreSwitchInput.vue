<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		:is-horizontal="true"
		class="CoreSwitchInput"
	>
		<div
			class="switch"
			:class="{ on: !!formValue }"
			tabindex="0"
			role="switch"
			:aria-checked="!!formValue"
			@click="handleToggle"
			@keydown.enter.space.prevent="handleToggle"
		>
			<div class="toggle"></div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { inject, onMounted } from "vue";
import { ref } from "vue";
import { FieldType } from "@/writerTypes";
import {
	accentColor,
	primaryTextColor,
	separatorColor,
	cssClasses,
} from "@/renderer/sharedStyleFields";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";
import { ComponentPublicInstance } from "vue";

const description = "A user input component with a simple on/off status.";

const onToggleHandlerStub = `
def handle_toggle(state, payload):

	# The payload will be a bool 

	state["its_on"] = payload`;

export default {
	writer: {
		name: "Switch Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			accentColor,
			primaryTextColor,
			separatorColor,
			cssClasses,
		},
		events: {
			"wf-toggle": {
				desc: "Sent when the switch is toggled.",
				stub: onToggleHandlerStub.trim(),
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const { formValue, handleInput, initializeFormValueBroker } =
	useFormValueBroker(wf, instancePath, rootInstance);

function handleToggle() {
	handleInput(!formValue.value, "wf-toggle");
}

onMounted(() => {
	initializeFormValueBroker();
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.switch {
	background: var(--separatorColor);
	width: 34px;
	height: 14px;
	border-radius: 14px;
	cursor: pointer;
}

.switch:focus-visible {
	outline: 1px solid var(--softenedAccentColor);
}

.switch.on {
	background: var(--softenedAccentColor);
}

.toggle {
	margin-top: -3px;
	width: 20px;
	height: 20px;
	background: var(--intensifiedSeparatorColor);
	border-radius: 10px;
	transition: 0.2s margin ease-in-out;
}

.switch.on .toggle {
	margin-left: 16px;
	background: var(--accentColor);
}
</style>
