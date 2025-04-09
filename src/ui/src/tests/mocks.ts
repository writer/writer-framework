import { generateCore } from "@/core";
import injectionKeys from "@/injectionKeys";
import { flattenInstancePath } from "@/renderer/instancePath";
import type { Component, InstancePath, UserFunction } from "@/writerTypes";
import { vi } from "vitest";
import { shallowRef } from "vue";
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
	const userState = shallowRef({});
	const sourceFiles = shallowRef<SourceFiles>({
		type: "directory",
		children: {},
	});
	const userFunctions = shallowRef<UserFunction[]>([]);
	const featureFlags = shallowRef<string[]>([]);
	const writerApplication = shallowRef<
		{ id: string; organizationId: string } | undefined
	>();

	core.userFunctions = userFunctions;
	core.userState = userState;
	core.sourceFiles = sourceFiles;
	core.featureFlags = featureFlags;
	core.writerApplication = writerApplication;

	vi.spyOn(core, "sendComponentUpdate").mockImplementation(async () => {});

	return {
		core,
		userState,
		sourceFiles,
		userFunctions,
		featureFlags,
		writerApplication,
	};
}

export const mockProvides: Record<symbol, unknown> = {
	[injectionKeys.componentId as symbol]: mockComponentId,
	[injectionKeys.instancePath as symbol]: mockInstancePath,
	[injectionKeys.flattenedInstancePath as symbol]:
		flattenInstancePath(mockInstancePath),
};
