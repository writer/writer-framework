/* eslint-disable @typescript-eslint/no-explicit-any */

import { describe, it, expect, vi } from "vitest";
import { ref, reactive, nextTick } from "vue";
import { useComponentFieldViewModel } from "./useComponentFieldViewModel";

type Component = { id: string; type: string; content: Record<string, string> };
type Defs = Record<string, { fields?: Record<string, { default?: string }> }>;

function mockDependencies(
	initial: Record<string, Component>,
	defs: Defs = {},
): { components: Record<string, Component>; wf: any; ssbm: any } {
	const components = reactive(initial);

	function getComponentById(id: string) {
		return components[id];
	}

	function getComponentDefinition(type?: string) {
		return type ? defs[type] : undefined;
	}

	return {
		components,
		wf: {
			getComponentById,
			getComponentDefinition,
			sendComponentUpdate: vi.fn(),
		},
		ssbm: {
			openMutationTransaction: vi.fn(),
			registerPreMutation: vi.fn(),
			registerPostMutation: vi.fn(),
			closeMutationTransaction: vi.fn(),
		},
	};
}

describe("useComponentFieldViewModel", () => {
	const componentId = "TestComponent";
	const fieldKey = "TestField";

	function setupMockDependencies(componentId: string, fieldKey: string) {
		return mockDependencies(
			{ [componentId]: { id: componentId, type: "Text", content: {} } },
			{ Text: { fields: { [fieldKey]: { default: "default test" } } } },
		);
	}

	it("Default: uses field default from component definition when content is unset", async () => {
		const dependencies = setupMockDependencies(componentId, fieldKey);

		const vm = useComponentFieldViewModel(
			{ componentId, fieldKey },
			dependencies,
		);

		await nextTick();

		expect(vm.value).toBe("default test");
	});

	it("Default update: reactive defaultValue overrides definition and updates value when changed", async () => {
		const dependencies = setupMockDependencies(componentId, fieldKey);

		const defaultValue = ref("ref default test");

		const vm = useComponentFieldViewModel(
			{ componentId, fieldKey, defaultValue },
			dependencies,
		);

		await nextTick();

		expect(vm.value).toBe("ref default test");

		defaultValue.value = "ref test";

		await nextTick();

		expect(vm.value).toBe("ref test");
	});

	it("viewModel update: setting vm.value persists to component content and reflects in getter", async () => {
		const dependencies = setupMockDependencies(componentId, fieldKey);

		const vm = useComponentFieldViewModel(
			{ componentId, fieldKey },
			dependencies,
		);

		await nextTick();

		expect(vm.value).toBe("default test");

		vm.value = "new value";

		await nextTick();

		expect(dependencies.components[componentId].content[fieldKey]).toBe(
			"new value",
		);

		expect(vm.value).toBe("new value");
	});
});
