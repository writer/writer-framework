import { useLogger } from "@/composables/useLogger";
import {
	deepMerge,
	getValueAtPath,
	isObject,
	setValueAtPath,
} from "@/utils/object";
import type { Component, Core } from "@/writerTypes";
import { MaybeRef, computed, unref } from "vue";

type UserState = Record<string, unknown>;

export function useBlueprintUserState(
	wf: Core,
	componentId: MaybeRef<string | undefined>,
	logger = useLogger(),
) {
	return computed<UserState>(() => {
		try {
			return getBlueprintUserState(wf, unref(componentId));
		} catch (e) {
			logger.error("Cannot compute Blueprint user state", e);
			return {};
		}
	});
}

function getBlueprintUserState(
	wf: Core,
	componentId: string | undefined,
): UserState {
	if (!componentId) return {};

	const component = wf.getComponentById(componentId);
	if (!component) return {};

	const isBlueprintNode = component.type.startsWith("blueprints_");
	if (!isBlueprintNode) return {};

	const state: UserState = {};

	for (const node of getDependentBlueprintsNodes(wf, componentId)) {
		if (node.type !== "blueprints_setstate" || !node.content) continue;
		const { element, valueType } = node.content;
		let value: unknown = node.content.value;

		const isInvalid = [element, value, valueType].some(
			(v) => typeof v !== "string",
		);
		if (isInvalid) continue;

		if (valueType === "JSON") {
			try {
				value = JSON.parse(String(value));
			} catch {
				value = {};
			}
		}

		const existingValue = getValueAtPath(state, element);
		if (existingValue !== undefined) {
			// as we get previous dependency by order of call, we keep the latest value, and merge with the previous ones if possible
			value =
				isObject(existingValue) && isObject(value)
					? deepMerge(value, existingValue)
					: existingValue;
		}

		setValueAtPath(state, element, value);
	}

	return state;
}

/**
 * Walk inside the component dependence tree
 */
function* getDependentBlueprintsNodes(
	wf: Core,
	componentId: string,
): Generator<Component> {
	const seenIds = new Set<string>();

	function* walk(id: string): Generator<Component> {
		if (seenIds.has(id)) return;
		seenIds.add(id);

		const c = wf.getComponentById(id);
		if (!c) return;

		for (const node of wf.getComponentsNested(c.parentId)) {
			if (node.outs?.some((o) => o.toNodeId === id)) {
				yield node;
				yield* walk(node.id);
			}
		}
	}

	yield* walk(componentId);
}
