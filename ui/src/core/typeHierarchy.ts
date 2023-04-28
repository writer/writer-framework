import { Component, ComponentMap } from "../streamsyncTypes";
import templateMap from "./templateMap";

function getDisallowedSet(
	components: ComponentMap,
	componentId: Component["id"]
): Set<Component["type"]> {
	const { type } = components[componentId];
	const supportedTypes = Object.keys(templateMap);
	const typesAndDefs = supportedTypes.map((type) => ({
		type,
		definition: templateMap[type]?.streamsync,
	}));
	const disallowedDefs = typesAndDefs.filter(
		(tad) =>
			tad.definition.allowedParentTypes &&
			!tad.definition.allowedParentTypes.includes(type)
	);
	const disallowed = new Set(disallowedDefs.map((tad) => tad.type));

	return disallowed;
}

function getAllowedSet(
	components: ComponentMap,
	componentId: Component["id"]
): Set<Component["type"]> {
	const { type, parentId } = components[componentId];
	const supportedTypes = Object.keys(templateMap);
	const { allowedChildrenTypes } = templateMap[type].streamsync;
	if (!allowedChildrenTypes) return new Set([]);

	let allowed = new Set<string>(allowedChildrenTypes);
	if (allowedChildrenTypes.includes("*")) {
		return new Set(supportedTypes);
	}
	if (allowed.delete("inherit")) {
		if (!parentId) return allowed;
		const parentContainable = getContainableTypes(components, parentId);
		allowed = new Set([...allowed, ...parentContainable]);
	}
	return allowed;
}

export function getContainableTypes(
	components: ComponentMap,
	componentId: Component["id"]
): Component["type"][] {
	const allowed = Array.from(getAllowedSet(components, componentId));
	const disallowed = Array.from(getDisallowedSet(components, componentId));
	const containable = allowed.filter((type) => !disallowed.includes(type));

	return containable;
}
