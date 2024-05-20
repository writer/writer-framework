<template>
	<textarea
		v-capture-tabs
		class="BuilderFieldsObject"
		variant="code"
		:value="component.content[fieldKey]"
		autocorrect="off"
		autocomplete="off"
		spellcheck="false"
		:placeholder="templateField.default"
		@input="
			(ev: Event) =>
				formatAndSetContentValue((ev.target as HTMLInputElement).value)
		"
	></textarea>
</template>

<script setup lang="ts">
import { toRefs, inject, computed } from "vue";
import { Component } from "../writerTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
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
@import "./sharedStyles.css";

.BuilderFieldsObject {
	padding: 16px 12px 12px 12px;
	font-size: inherit;
}
</style>
