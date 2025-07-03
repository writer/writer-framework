import { COMPONENT_TYPES_PAGE } from "@/constants/component";
import type { Core, Component } from "@/writerTypes";
import { computed, MaybeRef, unref } from "vue";

export function getComponentPage(
	wf: Core,
	componentId: Component["id"],
): Component | undefined {
	let currentId = unref(componentId);
	const visited = new Set();

	while (currentId && !visited.has(currentId)) {
		visited.add(currentId);
		const component = wf.getComponentById(currentId);
		if (!component) return;
		if (COMPONENT_TYPES_PAGE.has(component.type)) return component;
		currentId = component.parentId;
	}
	return undefined;
}

export function useComponentPage(
	wf: Core,
	componentId: MaybeRef<string | undefined>,
) {
	return computed(() => {
		const id = unref(componentId);
		return id ? getComponentPage(wf, id) : undefined;
	});
}
