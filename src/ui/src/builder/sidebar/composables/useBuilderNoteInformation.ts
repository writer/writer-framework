import type { generateCore } from "@/core";
import type { Component } from "@/writerTypes";
import { ComputedRef, Ref, computed } from "vue";

function getComponentRoot(
	wf: ReturnType<typeof generateCore>,
	componentId: string,
) {
	const component = wf.getComponentById(componentId);
	if (!component) return componentId;

	return getComponentRoot(wf, component.parentId) ?? componentId;
}

export function useBuilderNoteInformation(
	wf: ReturnType<typeof generateCore>,
	component: ComputedRef<Component> | Ref<Component>,
) {
	const formatter = new Intl.DateTimeFormat(undefined, {
		dateStyle: "short",
		timeStyle: "short",
	});

	const createdAt = computed(() => component.value.content.createdAt);
	const createdAtFormatted = computed(() => {
		if (!createdAt.value) return "";
		const date = new Date(createdAt.value);
		return formatter.format(date);
	});

	const type = computed<"ui" | "blueprints">(() => {
		const rootId = getComponentRoot(wf, component.value.id);
		return rootId === "blueprints_root" ? "blueprints" : "ui";
	});

	return {
		type,
		createdAt,
		createdAtFormatted,
	};
}
