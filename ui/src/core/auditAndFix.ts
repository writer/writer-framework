import {
	Component,
	ComponentMap,
	StreamsyncComponentDefinition,
} from "../streamsyncTypes";
import { getComponentDefinition } from "./templateMap";

/**
 * Audits integrity of ComponentMap. Applies automatic fixes if necessary.
 * Returns whether a fix was applied to the ComponentMap.
 *
 * @param components
 */
export function auditAndFixComponents(components: ComponentMap): boolean {
	let isFixApplied = false;
	Object.entries(components).forEach(([componentId, component]) => {
		if (componentId !== "root" && !components[component.parentId]) {
			console.warn(
				`Component ${component.id} (${component.type}). Orphan component.`
			);
		}
		isFixApplied =
			isFixApplied || auditAndFixPositions(component, components);
		auditComponent(component);
	});
	return isFixApplied;
}

export function auditComponent(component: Component) {
	const def = getComponentDefinition(component.type);
	if (!def) {
		console.error(
			`Component ${component.id} (${component.type}). Invalid component type.`
		);
		return;
	}

	auditComponentFieldKeys(component, def);
	auditComponentEventKeys(component, def);
	auditComponentBinding(component, def);
}

function auditComponentFieldKeys(
	component: Component,
	def: StreamsyncComponentDefinition
) {
	const fieldKeys = Object.keys(def.fields ?? {});
	if (!component.content) return;
	Object.keys(component.content).forEach((contentFieldKey) => {
		if (fieldKeys.includes(contentFieldKey)) return;
		console.warn(
			`Component ${component.id} (${component.type}). Field key "${contentFieldKey}" is defined in the component but not in the template.`
		);
	});
}

function auditComponentEventKeys(
	component: Component,
	def: StreamsyncComponentDefinition
) {
	const eventKeys = Object.keys(def.events ?? {});
	if (!component.handlers) return;
	Object.keys(component.handlers).forEach((handlerFieldKey) => {
		if (eventKeys.includes(handlerFieldKey)) return;
		console.warn(
			`Component ${component.id} (${component.type}). A handler is defined for "${handlerFieldKey}" but the template doesn't define that event.`
		);
	});
}

function auditComponentBinding(
	component: Component,
	def: StreamsyncComponentDefinition
) {
	const eventKeys = Object.keys(def.events ?? {});
	if (!component.binding) return;
	const boundEventType = component.binding.eventType;
	if (
		eventKeys.includes(boundEventType) &&
		def.events[boundEventType].bindable
	)
		return;
	console.warn(
		`Component ${component.id} (${component.type}). The component is bound to event "${component.binding.eventType}" but the template doesn't define that event or it's not bindable.`
	);
}

/**
 * A parent with broken positions e.g. 0, 1, 4, 5 can cause problems. This function
 * finds and fixes that problem if required.
 *
 * @param component
 * @param components
 * @returns
 */
function auditAndFixPositions(
	component: Component,
	components: ComponentMap
): boolean {
	let isFixApplied = false;
	if (component.id == "root") {
		if (component.position !== 0) {
			console.error("Root must be at position 0.");
		}
	}
	if (component.position == -1) {
		console.error(
			`Component ${component.id} (${component.type}). Invalid position.`
		);
	}

	const positionfulChildren = Object.values(components).filter(
		(c) => c.parentId === component.id && c.position !== -2
	);
	let positionSum = 0;
	positionfulChildren.forEach((c) => {
		positionSum += c.position;
	});

	const arithmeticProgression =
		((positionfulChildren.length - 1) * positionfulChildren.length) / 2;
	if (arithmeticProgression !== positionSum) {
		console.error(
			`Component ${component.id} (${component.type}). Invalid children positions. Automated fix will be applied.`
		);
		fixPositions(positionfulChildren);
		isFixApplied = true;
	}
	return isFixApplied;
}

function fixPositions(positionfulChildren: Component[]) {
	positionfulChildren.sort((a, b) => (a.position > b.position ? 1 : -1));
	positionfulChildren.map((component, index) => {
		component.position = index;
	});
}
