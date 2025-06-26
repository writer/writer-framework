import { useLogger } from "@/composables/useLogger";
import type { Component, Core } from "@/writerTypes";
import { computed } from "vue";
import merge from "lodash/merge";
import isPlainObject from "lodash/isPlainObject";
import {
	COMPONENT_TYPES_PAGE,
	COMPONENT_TYPES_ROOT,
} from "@/constants/component";
import { extractObjectPaths } from "@/utils/object";

type DynamicUserStateValue = {
	value: string;
	components: Component[];
};

export type DynamicUserState = Record<string, DynamicUserStateValue>;

export function useDynamicUserState(wf: Core, logger = useLogger()) {
	const userStateInitialPaths = computed(() => {
		return new Set(extractObjectPaths(wf.userStateInitial.value));
	});

	const blueprintsUserState = computed<DynamicUserState>(() => {
		try {
			return getBlueprintUserState(wf, userStateInitialPaths.value);
		} catch (e) {
			logger.error("Cannot compute Blueprint user state", e);
			return {};
		}
	});

	const bindingsUserState = computed<DynamicUserState>(() => {
		try {
			return getBindingsUserState(wf, userStateInitialPaths.value);
		} catch (e) {
			logger.error("Cannot compute Bindings user state", e);
			return {};
		}
	});

	const blueprintsResults = computed<DynamicUserState>(() => {
		try {
			return getBlueprintsResults(wf);
		} catch (e) {
			logger.error("Cannot compute Bindings user state", e);
			return {};
		}
	});

	return { blueprintsUserState, bindingsUserState, blueprintsResults };
}

function getBlueprintsResults(
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
			state[key] ??= { value: "unknown", components: [] };
			state[key].components.push(component);
		}
	}

	return state;
}

function getBindingsUserState(
	wf: Core,
	ignorePath = new Set<string>(),
): DynamicUserState {
	const state: DynamicUserState = {};

	for (const rootId of COMPONENT_TYPES_ROOT) {
		for (const component of wf.getComponentsNested(rootId)) {
			const key = component.binding?.stateRef;
			if (key && !ignorePath.has(key)) {
				state[key] ??= { value: "unknown", components: [] };
				state[key].components.push(component);
			}
		}
	}

	return state;
}

function getBlueprintUserState(
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
		const { element, valueType, value } = component.content;
		if (!element || typeof element !== "string") continue;
		if (ignorePath.has(element)) continue;

		let parsedValue: unknown = value;

		if (valueType === "JSON") {
			try {
				parsedValue = JSON.parse(String(value));
			} catch {
				parsedValue = {};
			}
		} else if (valueType === undefined || value === undefined) {
			parsedValue = "";
		}

		const existingValue = state[element];
		if (existingValue !== undefined) {
			parsedValue =
				isPlainObject(existingValue) && isPlainObject(parsedValue)
					? merge({}, existingValue, parsedValue)
					: parsedValue;
		}
		state[element] ??= { value: parsedValue, components: [] };
		state[element].components.push(component);
	}

	return state;
}
