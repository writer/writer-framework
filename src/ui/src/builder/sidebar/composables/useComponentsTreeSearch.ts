import type { generateCore } from "@/core";
import { computed, ComputedRef, Ref } from "vue";
import { Component } from "@/writerTypes";

export function useComponentsTreeSearch(
	wf: ReturnType<typeof generateCore>,
	query: ComputedRef<string> | Ref<string>,
) {
	function isComponentMatchingQuery(component: Component) {
		if (!query.value) return true;

		const def = wf.getComponentDefinition(component.type);
		if (def?.name.toLocaleLowerCase().includes(query.value)) return true;

		const matchingFields = Object.values(component.content).filter(
			(fieldContent) =>
				fieldContent.toLocaleLowerCase().includes(query.value),
		);
		if (matchingFields.length > 0) return true;

		return false;
	}

	return { isComponentMatchingQuery };
}

export function useComponentsTreeSearchResults(
	wf: ReturnType<typeof generateCore>,
	query: ComputedRef<string> | Ref<string>,
	rootId: ComputedRef<Component["id"]>,
) {
	const { isComponentMatchingQuery } = useComponentsTreeSearch(wf, query);

	const searchResultCount = computed<undefined | number>(() => {
		if (!query.value) return undefined;
		let count = 0;

		for (const c of wf.getComponentsNested(rootId.value)) {
			if (isComponentMatchingQuery(c)) count++;
		}
		return count;
	});

	return { searchResultCount };
}

export function useComponentsTreeSearchForComponent(
	wf: ReturnType<typeof generateCore>,
	query: ComputedRef<string> | Ref<string>,
	component: ComputedRef<Component>,
) {
	const { isComponentMatchingQuery } = useComponentsTreeSearch(wf, query);

	const matched = computed(
		() => !query.value || isComponentMatchingQuery(component.value),
	);

	const hasMatchingChildren = computed(() => {
		if (!query.value) return true;
		for (const c of wf.getComponentsNested(component.value.id)) {
			if (isComponentMatchingQuery(c)) return true;
		}
		return false;
	});

	return { hasMatchingChildren, matched };
}
