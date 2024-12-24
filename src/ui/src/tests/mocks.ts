import { generateCore } from "@/core";
import injectionKeys from "@/injectionKeys";
import { flattenInstancePath } from "@/renderer/instancePath";
import type { Component, InstancePath } from "@/writerTypes";
import { ref } from "vue";

export const mockComponentId = "component-id-test";

export const mockInstancePath: InstancePath = [
	{
		componentId: mockComponentId,
		instanceNumber: 0,
	},
];

export function buildMockComponent(component: Partial<Component>) {
	return {
		id: mockComponentId,
		content: {},
		parentId: "root",
		position: 0,
		type: "button",
		...component,
	};
}

export function buildMockCore() {
	const core = generateCore();
	const userState = ref({});

	core.userState = ref(userState);

	return { core, userState };
}

export const mockProvides: Record<symbol, unknown> = {
	[injectionKeys.componentId as symbol]: mockComponentId,
	[injectionKeys.instancePath as symbol]: mockInstancePath,
	[injectionKeys.flattenedInstancePath as symbol]:
		flattenInstancePath(mockInstancePath),
};
