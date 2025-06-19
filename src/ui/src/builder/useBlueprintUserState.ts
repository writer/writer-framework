import { useLogger } from "@/composables/useLogger";
import type { Core } from "@/writerTypes";
import { computed } from "vue";
import set from "lodash/set";
import get from "lodash/get";
import merge from "lodash/merge";
import isPlainObject from "lodash/isPlainObject";

type UserState = Record<string, unknown>;

export function useBlueprintUserState(wf: Core, logger = useLogger()) {
	return computed<UserState>(() => {
		try {
			return getBlueprintUserState(wf);
		} catch (e) {
			logger.error("Cannot compute Blueprint user state", e);
			return {};
		}
	});
}

function getBlueprintUserState(wf: Core): UserState {
	const state: UserState = {};

	function* getSetStateNode() {
		for (const node of wf.getComponentsNested("blueprints_root")) {
			if (node.type === "blueprints_setstate" && node.content) {
				yield node.content;
			}
		}
	}

	for (const { element, valueType, value } of getSetStateNode()) {
		const isInvalid = [element, value, valueType].some(
			(v) => typeof v !== "string",
		);
		if (isInvalid) continue;

		let parsedValue: unknown = value;

		if (valueType === "JSON") {
			try {
				parsedValue = JSON.parse(String(value));
			} catch {
				parsedValue = {};
			}
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
