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

function formatGraphIds(graphIds: unknown): string | null {
	if (!graphIds) return null;

	if (Array.isArray(graphIds) && graphIds.length > 0) {
		const ids = graphIds.filter(
			(id) => typeof id === "string" && !id.startsWith("@{"),
		);
		return ids.length > 0 ? ids.join(", ") : null;
	}

	if (typeof graphIds === "string" && !graphIds.startsWith("@{")) {
		return graphIds;
	}

	return null;
}

function isFunctionTool(tool: unknown): boolean {
	return (
		tool !== null &&
		typeof tool === "object" &&
		"type" in tool &&
		tool.type === "function"
	);
}

function formatToolName(toolName: string, tool: unknown): string {
	if (!tool || typeof tool !== "object" || !("type" in tool)) {
		return toolName;
	}

	if (tool.type === "graph" && "graph_ids" in tool) {
		const formattedIds = formatGraphIds(tool.graph_ids);
		if (formattedIds) {
			return `${toolName} (${formattedIds})`;
		}
	}

	return toolName;
}

const nonFunctionToolKeys = computed(() => {
	return Object.keys(tools.value).filter((toolName) => {
		return !isFunctionTool(tools.value[toolName]);
	});
});

const displayText = computed(() => {
	if (nonFunctionToolKeys.value.length > 0) {
		return nonFunctionToolKeys.value
			.map((toolName) => formatToolName(toolName, tools.value[toolName]))
			.join(", ");
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
