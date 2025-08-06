import { COMPONENT_TYPES_PAGE } from "@/constants/component";
import type { Component, WriterComponentDefinition } from "@/writerTypes";
import { computed, MaybeRef, unref } from "vue";

export function useBlueprintComponentResultId(
	component: MaybeRef<Component>,
	definition: MaybeRef<WriterComponentDefinition>,
) {
	return computed(() => {
		const { type, id } = unref(component) ?? {};
		const outs = unref(definition)?.outs;

		const hasResultId =
			type &&
			!COMPONENT_TYPES_PAGE.has(type) &&
			type.startsWith("blueprints_") &&
			outs?.["success"] !== undefined;

		return hasResultId ? `@{results.${id}}` : "";
	});
}
