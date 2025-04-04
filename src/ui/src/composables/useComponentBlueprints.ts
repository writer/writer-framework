import type { Core, Component } from "@/writerTypes";
import { computed, ComputedRef, unref } from "vue";

export function useComponentLinkedWorkflows(
	wf: Core,
	componentId: ComputedRef<string> | string,
	eventType: ComputedRef<string> | string,
) {
	function isWorkflowTrigger(c: Component) {
		return (
			c.type === "workflows_uieventtrigger" &&
			c.content.refComponentId === unref(componentId) &&
			c.content.refEventType === unref(eventType)
		);
	}

	const workflows = computed<Component[]>(() => {
		const workflowIds = new Set(triggers.value.map((c) => c.parentId));

		return [...workflowIds]
			.map((i) => wf.getComponentById(i))
			.filter(Boolean);
	});

	const triggers = computed<Component[]>(() => {
		return wf
			.getComponents("workflows_root")
			.flatMap((w) => wf.getComponents(w.id).filter(isWorkflowTrigger));
	});

	const isLinked = computed(() => triggers.value.length > 0);

	return { workflows, triggers, isLinked };
}
