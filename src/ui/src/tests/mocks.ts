import { generateCore } from "@/core";
import injectionKeys from "@/injectionKeys";
import { flattenInstancePath } from "@/renderer/instancePath";
import type { Component, InstancePath, UserFunction } from "@/writerTypes";
import { vi } from "vitest";
import { ref } from "vue";
import { SourceFiles } from "../writerTypes";

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
	const sourceFiles = ref<SourceFiles>({ type: "directory", children: {} });
	const userFunctions = ref<UserFunction[]>([]);
	const featureFlags = ref<string[]>([]);

	core.userFunctions = userFunctions;
	core.userState = userState;
	core.sourceFiles = sourceFiles;
	core.featureFlags = featureFlags;

	vi.spyOn(core, "sendComponentUpdate").mockImplementation(async () => {});

	return { core, userState, sourceFiles, userFunctions, featureFlags };
}

export const mockProvides: Record<symbol, unknown> = {
	[injectionKeys.componentId as symbol]: mockComponentId,
	[injectionKeys.instancePath as symbol]: mockInstancePath,
	[injectionKeys.flattenedInstancePath as symbol]:
		flattenInstancePath(mockInstancePath),
};
