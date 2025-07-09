import type { Core, Component } from "@/writerTypes";

/**
 * Walk inside the component dependence tree
 */
export function* getDependentBlueprintsNodes(
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
