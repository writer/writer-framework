<template>
	<div class="BuilderFieldsTools" :data-automation-key="props.fieldKey">
		Tools
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed } from "vue";
import { Component, FieldControl } from "@/writerTypes";
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

const handleInput = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};
</script>

<style>
.BuilderFieldsTool {
}
</style>

<style scoped>
@import "./sharedStyles.css";
</style>
