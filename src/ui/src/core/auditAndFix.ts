import {
	Component,
	ComponentMap,
	WriterComponentDefinition,
} from "@/writerTypes";
import { getComponentDefinition } from "./templateMap";
import { useLogger } from "@/composables/useLogger";

/**
 * Audits integrity of ComponentMap. Applies automatic fixes if necessary.
 * Returns whether a fix was applied to the ComponentMap.
 *
 * @param components
 */
export function auditAndFixComponents(components: ComponentMap): boolean {
	let isFixApplied = false;
	auditOrphanComponents(components);
	Object.entries(components).forEach(([, component]) => {
		isFixApplied =
			auditAndFixPositions(component, components) || isFixApplied;
		isFixApplied = auditAndFixComponent(component) || isFixApplied;
	});
	return isFixApplied;
}

export function auditAndFixComponent(component: Component): boolean {
	const logger = useLogger();

	const def = getComponentDefinition(component.type);
	if (!def || def.category == "Fallback") {
		logger.error(
			`Component ${component.id} (${component.type}). Invalid component type.`,
		);
		return false;
	}

	let isFixApplied = false;
	isFixApplied = fixComponentDeprecatedContent(component, def);
	isFixApplied = fixComponentDeprecatedPrefixes(component) || isFixApplied;
	auditComponentFieldKeys(component, def);
	auditComponentBinding(component, def);
	return isFixApplied;
}

function traverseComponentTree(
	parentId: Component["id"],
	components: ComponentMap,
	visited: Record<string, boolean> = {},
) {
	visited[parentId] = true;
	Object.entries(components)
		.filter(([, component]) => component.parentId === parentId)
		.forEach(([componentId]) =>
			traverseComponentTree(componentId, components, visited),
		);
}

function auditOrphanComponents(components: ComponentMap) {
	const logger = useLogger();
	const visited = Object.fromEntries(
		Object.entries(components).map(([componentId]) => [componentId, false]),
	);
	traverseComponentTree("root", components, visited);
	traverseComponentTree("blueprints_root", components, visited);
	Object.entries(visited).forEach(([componentId, isVisited]) => {
		if (!isVisited) {
			logger.warn(
				`Component ${componentId} (${components[componentId].type}). Orphan component.`,
			);
		}
	});
}

function auditComponentFieldKeys(
	component: Component,
	def: WriterComponentDefinition,
) {
	const logger = useLogger();
	const fieldKeys = Object.keys(def.fields ?? {});
	if (!component.content) return;
	Object.keys(component.content).forEach((contentFieldKey) => {
		if (fieldKeys.includes(contentFieldKey)) return;
		logger.warn(
			`Component ${component.id} (${component.type}). Field key "${contentFieldKey}" is defined in the component but not in the template.`,
		);
	});
}

function auditComponentBinding(
	component: Component,
	def: WriterComponentDefinition,
) {
	const eventKeys = Object.keys(def.events ?? {});
	if (!component.binding) return;
	const boundEventType = component.binding.eventType;
	if (
		eventKeys.includes(boundEventType) &&
		def.events[boundEventType].bindable
	)
		return;
	const logger = useLogger();
	logger.warn(
		`Component ${component.id} (${component.type}). The component is bound to event "${component.binding.eventType}" but the template doesn't define that event or it's not bindable.`,
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
	components: ComponentMap,
): boolean {
	const logger = useLogger();
	let isFixApplied = false;
	if (component.id == "root") {
		if (component.position !== 0) {
			logger.error("Root must be at position 0.");
		}
	}
	if (component.position == -1) {
		logger.error(
			`Component ${component.id} (${component.type}). Invalid position.`,
		);
	}

	const positionfulChildren = Object.values(components).filter(
		(c) =>
			c.parentId === component.id &&
			c.position !== -2 &&
			!c.isCodeManaged,
	);
	let positionSum = 0;
	positionfulChildren.forEach((c) => {
		positionSum += c.position;
	});

	const arithmeticProgression =
		((positionfulChildren.length - 1) * positionfulChildren.length) / 2;
	if (arithmeticProgression !== positionSum) {
		logger.error(
			`Component ${component.id} (${component.type}). Invalid children positions. Automated fix will be applied.`,
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

function fixComponentDeprecatedPrefixes(component: Component) {
	let isFixApplied = false;
	Object.keys(component.handlers ?? {}).forEach((eventName) => {
		if (!eventName.startsWith("ss-")) return;
		const newEventName = `wf-${eventName.substring(3)}`;
		component.handlers[newEventName] = component.handlers[eventName];
		isFixApplied = true;
		delete component.handlers[eventName];
	});

	if (component.binding?.eventType?.startsWith("ss-")) {
		const eventName = component.binding?.eventType;
		const newEventName = `wf-${eventName.substring(3)}`;
		component.binding.eventType = newEventName;
		isFixApplied = true;
	}

	return isFixApplied;
}

/**
 * Corrects the mapping of deprecated properties following component changes.
 *
 * @param component
 * @param def
 */
function fixComponentDeprecatedContent(
	component: Component,
	def: WriterComponentDefinition,
) {
	let isFixApplied = false;
	if (component.type == "column") {
		if ("horizontalAlignment" in component.content) {
			const mapping = {
				left: "start",
				center: "center",
				right: "end",
			};

			component.content["contentHAlign"] =
				mapping[component.content["horizontalAlignment"]] ||
				component.content["horizontalAlignment"];
			delete component.content["horizontalAlignment"];
			isFixApplied = true;
		}
		if ("verticalAlignment" in component.content) {
			const mapping = {
				normal: "unset",
				top: "start",
				center: "center",
				bottom: "end",
			};

			component.content["contentVAlign"] =
				mapping[component.content["verticalAlignment"]] ||
				component.content["verticalAlignment"];
			delete component.content["verticalAlignment"];
			isFixApplied = true;
		}
	} else if (component.type == "horizontalstack") {
		if ("alignment" in component.content) {
			const mapping = {
				left: "start",
				center: "center",
				right: "end",
			};

			component.content["contentHAlign"] =
				mapping[component.content["alignment"]] ||
				component.content["alignment"];
			delete component.content["alignment"];
			isFixApplied = true;
		}
	} else if (component.type == "section") {
		if ("snapMode" in component.content) {
			delete component.content["snapMode"];
			isFixApplied = true;
		}
	}
	return isFixApplied;
}
