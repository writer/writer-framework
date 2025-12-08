import type { Component } from "@/writerTypes";

export const SHARED_BLUEPRINT_FLAG_VALUE = "true";

/**
 * Returns true when the component represents a shared blueprint.
 * Normalizes the stored string flag to a boolean for consumers.
 */
export function isSharedBlueprint(component?: Component | null): boolean {
	const flag = component?.content?.isSharedBlueprint;
	return String(flag) === SHARED_BLUEPRINT_FLAG_VALUE;
}
