import { useLogger } from "@/composables/useLogger";
import type { Component, Core } from "@/writerTypes";
import { computed } from "vue";
import {
	COMPONENT_TYPES_PAGE,
	COMPONENT_TYPES_ROOT,
} from "@/constants/component";
import { extractObjectPaths } from "@/utils/object";

type DynamicUserStateValue = {
	components: Component[];
};

export type DynamicUserState = Record<string, DynamicUserStateValue>;

export function useDynamicUserState(wf: Core, logger = useLogger()) {
	const userStateInitialPaths = computed(() => {
		return new Set(extractObjectPaths(wf.userStateInitial.value));
	});

	const blueprintsSetStates = computed<DynamicUserState>(() => {
		try {
			return computeBlueprintsSetStates(wf, userStateInitialPaths.value);
		} catch (e) {
			logger.error("Cannot compute Blueprint user state", e);
			return {};
		}
	});

	const bindings = computed<DynamicUserState>(() => {
		try {
			return computeBindings(wf, userStateInitialPaths.value);
		} catch (e) {
			logger.error("Cannot compute Bindings user state", e);
			return {};
		}
	});

	const blueprintsResults = computed<DynamicUserState>(() => {
		try {
			return computeBlueprintsResults(wf);
		} catch (e) {
			logger.error("Cannot compute Bindings user state", e);
			return {};
		}
	});

	return { blueprintsSetStates, bindings, blueprintsResults };
}

function computeBlueprintsResults(
	wf: Core,
	ignorePath = new Set<string>(),
): DynamicUserState {
	const state: DynamicUserState = {};

	for (const component of wf.getComponentsNested("blueprints_root")) {
		const componentType = component.type;
		const componentDefinition = wf.getComponentDefinition(component.type);
		if (!componentDefinition) continue;

		const hasResultId =
			component.type &&
			!COMPONENT_TYPES_PAGE.has(componentType) &&
			component.type.startsWith("blueprints_") &&
			componentDefinition?.outs?.["success"] !== undefined;

		if (!hasResultId) continue;

		const key = `results.${component.id}`;
		if (key && !ignorePath.has(key)) {
			state[key] ??= { components: [] };
			state[key].components.push(component);
		}
	}

	return state;
}

function computeBindings(
	wf: Core,
	ignorePath = new Set<string>(),
): DynamicUserState {
	const state: DynamicUserState = {};

	for (const rootId of COMPONENT_TYPES_ROOT) {
		for (const component of wf.getComponentsNested(rootId)) {
			const key = component.binding?.stateRef;
			if (key && !ignorePath.has(key)) {
				state[key] ??= { components: [] };
				state[key].components.push(component);
			}
		}
	}

	return state;
}

function computeBlueprintsSetStates(
	wf: Core,
	ignorePath = new Set<string>(),
): DynamicUserState {
	function* getSetStateContent() {
		for (const node of wf.getComponentsNested("blueprints_root")) {
			if (node.type === "blueprints_setstate" && node.content) {
				yield node;
			}
		}
	}

	const state: DynamicUserState = {};

	for (const component of getSetStateContent()) {
		const element = component.content?.element;
		if (!element || typeof element !== "string") continue;
		if (ignorePath.has(element)) continue;

		state[element] ??= { components: [] };
		state[element].components.push(component);
	}

	return state;
}
