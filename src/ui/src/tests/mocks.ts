import { generateCore } from "@/core";
import injectionKeys from "@/injectionKeys";
import { flattenInstancePath } from "@/renderer/instancePath";
import type { Component, InstancePath, UserFunction } from "@/writerTypes";
import { vi } from "vitest";
import { computed, ref, shallowRef } from "vue";
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
	const mode = ref<"run" | "edit">("run");
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
	core.userFunctions = userFunctions;
	core.userState = userState;
	core.sourceFiles = sourceFiles;
	core.featureFlags = featureFlags;
	core.writerApplication = writerApplication;
	core.mode = mode;

	core.isWriterCloudApp = computed(
		() => writerApplication.value !== undefined,
	);
	core.writerOrgId = computed(
		() => Number(writerApplication.value?.organizationId) || undefined,
	);
	core.writerAppId = computed(() => writerApplication.value?.id);

	vi.spyOn(core, "sendComponentUpdate").mockImplementation(async () => {});

	return {
		core,
		mode,
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
