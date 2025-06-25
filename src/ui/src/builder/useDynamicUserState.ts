import { useLogger } from "@/composables/useLogger";
import type { Core } from "@/writerTypes";
import { computed } from "vue";
import set from "lodash/set";
import get from "lodash/get";
import merge from "lodash/merge";
import isPlainObject from "lodash/isPlainObject";
import { COMPONENT_TYPES_ROOT } from "@/constants/component";

type UserState = Record<string, unknown>;

export function useDynamicUserState(wf: Core, logger = useLogger()) {
	const blueprintsUserState = computed<UserState>(() => {
		try {
			return getBlueprintUserState(wf);
		} catch (e) {
			logger.error("Cannot compute Blueprint user state", e);
			return {};
		}
	});

	const bindingsUserState = computed<UserState>(() => {
		try {
			return getBindingsUserState(wf);
		} catch (e) {
			logger.error("Cannot compute Bindings user state", e);
			return {};
		}
	});

	return { blueprintsUserState, bindingsUserState };
}

function getBindingsUserState(wf: Core): UserState {
	const state: UserState = {};

	for (const rootId of COMPONENT_TYPES_ROOT) {
		for (const component of wf.getComponentsNested(rootId)) {
			if (component.binding?.stateRef) {
				set(state, component.binding?.stateRef, "unknown value");
			}
		}
	}

	return state;
}

function getBlueprintUserState(wf: Core): UserState {
	const state: UserState = {};

	function* getSetStateContent() {
		for (const node of wf.getComponentsNested("blueprints_root")) {
			if (node.type === "blueprints_setstate" && node.content) {
				yield node.content;
			}
		}
	}

	for (const { element, valueType, value } of getSetStateContent()) {
		if (!element || typeof element !== "string") continue;

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

		const existingValue = get(state, element);
		if (existingValue !== undefined) {
			parsedValue =
				isPlainObject(existingValue) && isPlainObject(parsedValue)
					? merge({}, existingValue, parsedValue)
					: parsedValue;
		}
		set(state, element, parsedValue);
	}

	return state;
}
