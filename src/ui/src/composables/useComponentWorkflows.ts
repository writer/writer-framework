import type { Core, Component } from "@/writerTypes";
import { computed, ComputedRef, unref } from "vue";

export function useComponentLinkedWorkflows(
	wf: Core,
	componentId: ComputedRef<string> | string,
	eventType: ComputedRef<string> | string,
) {
	return computed<Component[]>(() => {
		return wf
			.getComponents("workflows_root")
			.filter((w) =>
				wf
					.getComponents(w.id)
					.some(
						(c) =>
							c.type === "workflows_uieventtrigger" &&
							c.content.refComponentId === unref(componentId) &&
							c.content.refEventType === unref(eventType),
					),
			);
	});
}
