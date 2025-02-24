<template>
	<div
		class="BuilderFieldsWriterGraphId"
		:data-automation-key="props.fieldKey"
	>
		<BuilderGraphSelect v-model="selectedGraph" />
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, PropType } from "vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderGraphSelect from "../BuilderGraphSelect.vue";

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

const selectedGraph = computed<string>({
	get: () => component.value.content[props.fieldKey] ?? "",
	set(value) {
		setContentValue(component.value.id, fieldKey.value, String(value));
	},
});
</script>
