<template>
	<div class="BuilderFieldsText" :data-automation-key="props.fieldKey">
		<template
			v-if="
				!templateField.control ||
				templateField.control == FieldControl.Text
			"
		>
			<BuilderTemplateInput
				class="content"
				:input-id="inputId"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				:options="options"
				@input="handleInput"
			/>
		</template>
		<template v-else-if="templateField.control == FieldControl.Textarea">
			<BuilderTemplateInput
				multiline
				variant="text"
				class="content"
				:input-id="inputId"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				@input="handleInput"
			/>
		</template>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed } from "vue";
import { Component, FieldControl } from "../writerTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));
const templateField = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition.fields[fieldKey.value];
});

const inputId = computed(() => `${props.componentId}-${props.fieldKey}`);

const options = computed(() => {
	const field = templateField.value;
	if (field.options) {
		return typeof field.options === "function"
			? field.options(wf, componentId.value)
			: field.options;
	}
	return {};
});

const handleInput = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};
</script>

<style>
.BuilderFieldsText .content {
	padding: 16px 12px 12px 12px;
	width: 100%;
}
</style>

<style scoped>
@import "./sharedStyles.css";
</style>
