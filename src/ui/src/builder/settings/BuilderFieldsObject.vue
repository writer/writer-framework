<template>
	<BuilderTemplateInput
		class="BuilderFieldsObject"
		:data-automation-key="props.fieldKey"
		multiline
		variant="code"
		:value="component.content[fieldKey]"
		:placeholder="templateField?.default"
		:error="error"
		@input="
			(ev: Event) =>
				formatAndSetContentValue((ev.target as HTMLInputElement).value)
		"
	/>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, PropType } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import { Component } from "@/writerTypes";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
});
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const formatAndSetContentValue = (value: string) => {
	setContentValue(component.value.id, fieldKey.value, value);
};

const templateField = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition.fields[fieldKey.value];
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsObject {
	font-size: inherit;
}
</style>
