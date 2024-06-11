<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		:is-horizontal="true"
		class="CoreSwitchInput"
	>
		<div
			class="switch"
			:class="{ on: toggleValue }"
			tabindex="0"
			role="switch"
			:aria-checked="toggleValue"
			@click="handleToggle"
			@keydown.enter.space.prevent="handleToggle"
		>
			<div class="toggle"></div>
		</div>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { inject } from "vue";
import { ref } from "vue";
import { FieldType } from "../../writerTypes";
import {
	accentColor,
	primaryTextColor,
	separatorColor,
	cssClasses,
} from "../../renderer/sharedStyleFields";
import { onMounted } from "vue";
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
const toggleValue = ref(false);

function handleToggle() {
	toggleValue.value = !toggleValue.value;
	handleInput(toggleValue.value, "wf-toggle");
}

onMounted(() => {
	toggleValue.value = !!formValue.value;
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

.CoreSwitchInput {
}

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
