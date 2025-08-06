import { Component, Core } from "@/writerTypes";
import { computed, MaybeRef, unref } from "vue";

export function useComponentInformation(
	wf: Core,
	componentId: MaybeRef<Component["id"] | undefined>,
) {
	const component = computed(() => {
		const id = unref(componentId);
		if (!id) return;
		return wf.getComponentById(id);
	});

	const definition = computed(() => {
		const type = component.value?.type;
		if (!type) return;
		return wf.getComponentDefinition(type);
	});

	return { component, definition };
}
