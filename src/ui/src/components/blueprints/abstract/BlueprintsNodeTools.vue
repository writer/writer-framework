<script setup lang="ts">
import { computed } from "vue";
import { FieldType } from "@/writerTypes";
import { parseToolsField } from "@/composables/useBlueprintNodeTools";

const props = defineProps<{
	fieldKey: string;
	fieldType: string;
	fieldValue: unknown;
	hasOutputs: boolean;
}>();

const hasToolsButNoFunctionTools = computed(() => {
	if (props.fieldType !== FieldType.Tools) return false;
	const tools = parseToolsField(props.fieldValue);
	const toolKeys = Object.keys(tools);
	if (toolKeys.length === 0) return false;
	return !toolKeys.some((key) => tools[key]?.type === "function");
});

const displayText = computed(() => {
	if (!props.hasOutputs && hasToolsButNoFunctionTools.value) {
		return "No outputs";
	}
	return "None configured.";
});
</script>

<template>
	<div
		v-if="!hasOutputs"
		class="BlueprintsNode__main__outputs__output BlueprintsNode__main__outputs__empty"
	>
		{{ displayText }}
	</div>
</template>

<style scoped>
.BlueprintsNode__main__outputs__empty {
	margin-right: 5px;
}
</style>
