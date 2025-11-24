import { computed, type ComputedRef } from "vue";
import { FieldType, WriterComponentDefinition } from "@/writerTypes";

type Tool = {
	type: "function" | "graph" | "web_search";
	[key: string]: unknown;
};

type ToolsRecord = Record<string, Tool>;

export function parseToolsField(fieldValue: unknown): ToolsRecord {
	if (!fieldValue) return {};

	if (typeof fieldValue === "string") {
		try {
			const parsed = JSON.parse(fieldValue);
			return typeof parsed === "object" && parsed !== null
				? (parsed as ToolsRecord)
				: {};
		} catch {
			return {};
		}
	}

	if (typeof fieldValue === "object") {
		return fieldValue as ToolsRecord;
	}

	return {};
}

export function useBlueprintNodeTools(
	def: ComputedRef<WriterComponentDefinition | undefined>,
	fields: Record<string, { value: unknown }>,
) {
	const hasOnlyNonFunctionTools = computed(() => {
		const toolsFields = Object.entries(def.value?.fields ?? {}).filter(
			([_, field]) => field.type === FieldType.Tools,
		);

		if (toolsFields.length === 0) return false;

		const parsedTools = toolsFields.map(([fieldKey]) => ({
			fieldKey,
			tools: parseToolsField(fields[fieldKey]?.value),
		}));

		const hasAnyTools = parsedTools.some(
			({ tools }) => Object.keys(tools).length > 0,
		);

		if (!hasAnyTools) return false;

		return parsedTools.every(({ tools }) => {
			const toolKeys = Object.keys(tools);
			if (toolKeys.length === 0) return true;

			return !toolKeys.some((key) => tools[key]?.type === "function");
		});
	});

	function hasToolsButNoFunctionTools(fieldKey: string): boolean {
		const tools = parseToolsField(fields[fieldKey]?.value);
		const toolKeys = Object.keys(tools);
		if (toolKeys.length === 0) return false;
		return !toolKeys.some((key) => tools[key]?.type === "function");
	}

	return {
		hasOnlyNonFunctionTools,
		hasToolsButNoFunctionTools,
	};
}

