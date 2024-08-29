<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreColorInput"
	>
		<BaseInputColor
			:value="formValue"
			:custom-colors="colorList"
			@update:value="handleInput($event, 'wf-change')"
			@change="handleInput($event, 'wf-change-finish')"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { ComponentPublicInstance } from "vue";
import { cssClasses } from "@/renderer/sharedStyleFields";
import { FieldType, WriterComponentDefinition } from "@/writerTypes";
import BaseInputColor from "../base/BaseInputColor.vue";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const description =
	"A user input component that allows users to select a color using a color picker interface.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_color" to the new value, provided as string.

	state["new_color"] = payload`;

const definition = {
	name: "Color Input",
	description,
	category: "Input",
	fields: {
		label: {
			name: "Label",
			init: "Input Label",
			type: FieldType.Text,
		},
		colorList: {
			name: "Color List",
			desc: "List of predefined colors",
			type: FieldType.Object,
			init: JSON.stringify([
				"#5551ff",
				"#3be19b",
				"#ff3d00",
				"#333333",
				"#0094d1",
			]),
		},
		cssClasses,
	},
	events: {
		"wf-change": {
			desc: "Capture changes as they happen.",
			stub: onChangeHandlerStub,
			bindable: true,
		},
		"wf-change-finish": {
			desc: "Capture changes once this control has lost focus.",
			stub: onChangeHandlerStub,
		},
	},
} satisfies WriterComponentDefinition;

export default { writer: definition };
</script>
<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useFormValueBroker } from "@/renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const colorList = computed(() =>
	Array.isArray(fields.colorList.value) ? fields.colorList.value : undefined,
);

const { formValue, handleInput } = useFormValueBroker<string>(
	wf,
	instancePath,
	rootInstance,
);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";
@import "@/renderer/colorTransformations.css";

.CoreColorInput {
	width: fit-content;
}
</style>
