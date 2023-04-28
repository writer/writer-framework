<template>
	<textarea
		class="BuilderFieldsObject"
		v-capture-tabs
		variant="code"
		:value="component.content[fieldKey]"
		v-on:input="(ev:Event) => formatAndSetContentValue((ev.target as HTMLInputElement).value)"
		autocorrect="off"
		autocomplete="off"
		spellcheck="false"
		:placeholder="templateField.default"
	></textarea>
</template>

<script setup lang="ts">
import { toRefs, inject, computed } from "vue";
import { Component } from "../streamsyncTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));

const formatAndSetContentValue = (value: string) => {
	setContentValue(component.value.id, fieldKey.value, value);
};

const templateField = computed(() => {
	const { type } = component.value;
	const definition = ss.getComponentDefinition(type);
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
