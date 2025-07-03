import { COMPONENT_TYPES_PAGE } from "@/constants/component";
import type { Core, Component } from "@/writerTypes";
import { computed, MaybeRef, unref } from "vue";

export function useComponentPage(
	wf: Core,
	componentId: MaybeRef<string | undefined>,
) {
	const page = computed<Component | undefined>(() => {
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
	});

	const childrenIds = computed(() => {
		const ids = new Set();

		if (!page.value) return ids;

		for (const child of wf.getComponentsNested(page.value.id, {
			includeBMC: true,
			includeCMC: true,
		})) {
			ids.add(child.id);
		}
		return ids;
	});

	function isInside(componentId: string) {
		if (!page.value) return false;
		return childrenIds.value.has(componentId);
	}

	return { page, isInside };
}
