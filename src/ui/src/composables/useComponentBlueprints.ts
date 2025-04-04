import type { Core, Component } from "@/writerTypes";
import { computed, ComputedRef, unref } from "vue";

export function useComponentLinkedBlueprints(
	wf: Core,
	componentId: ComputedRef<string> | string,
	eventType: ComputedRef<string> | string,
) {
	function isBlueprintTrigger(c: Component) {
		return (
			c.type === "blueprints_uieventtrigger" &&
			c.content.refComponentId === unref(componentId) &&
			c.content.refEventType === unref(eventType)
		);
	}

	const blueprints = computed<Component[]>(() => {
		const blueprintIds = new Set(triggers.value.map((c) => c.parentId));

		return [...blueprintIds]
			.map((i) => wf.getComponentById(i))
			.filter(Boolean);
	});

	const triggers = computed<Component[]>(() => {
		return wf
			.getComponents("blueprints_root")
			.flatMap((w) => wf.getComponents(w.id).filter(isBlueprintTrigger));
	});

	const isLinked = computed(() => triggers.value.length > 0);

	return { blueprints, triggers, isLinked };
}
