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

const tools = computed(() => {
	if (props.fieldType !== FieldType.Tools) return {};
	return parseToolsField(props.fieldValue);
});

const hasToolsButNoFunctionTools = computed(() => {
	if (props.fieldType !== FieldType.Tools) return false;
	const toolKeys = Object.keys(tools.value);
	if (toolKeys.length === 0) return false;
	return !toolKeys.some((key) => tools.value[key]?.type === "function");
});

function isFunctionTool(tool: unknown): boolean {
	return (
		tool !== null &&
		typeof tool === "object" &&
		"type" in tool &&
		tool.type === "function"
	);
}

const nonFunctionToolKeys = computed(() => {
	return Object.keys(tools.value).filter((toolName) => {
		return !isFunctionTool(tools.value[toolName]);
	});
});

const displayText = computed(() => {
	if (nonFunctionToolKeys.value.length > 0) {
		return nonFunctionToolKeys.value.join(", ");
	}

	if (!props.hasOutputs && hasToolsButNoFunctionTools.value) {
		return "No outputs";
	}

	return "None configured.";
});

const shouldRender = computed(() => {
	return !props.hasOutputs || nonFunctionToolKeys.value.length > 0;
});
</script>

<template>
	<div
		v-if="shouldRender"
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
