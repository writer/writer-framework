import { describe, it, expect } from "vitest";
import { ref, nextTick } from "vue";
import { buildMockComponent, buildMockCore } from "@/tests/mocks";
import { generateBuilderManager } from "./builderManager";
import {
	useComponentFieldViewModel,
	Dependencies,
} from "./useComponentFieldViewModel";
import { FieldType, WriterComponentDefinition } from "@/writerTypes";

describe(useComponentFieldViewModel.name, () => {
	const componentId = "TestComponent";
	const fieldKey = "TestField";

	let mockCore: ReturnType<typeof buildMockCore>;

	function setupMockDependencies(
		componentId: string,
		fieldKey: string,
	): Dependencies {
		mockCore = buildMockCore();
		mockCore.core.addComponent(
			buildMockComponent({
				id: componentId,
				type: FieldType.Text,
				content: {
					[fieldKey]: undefined,
				},
			}),
		);

		function getComponentDefinition(): WriterComponentDefinition {
			return {
				name: "",
				description: "",
				fields: {
					[fieldKey]: {
						name: "",
						type: FieldType.Text,
						default: "default test",
					},
				},
			};
		}

		return {
			wf: {
				...mockCore.core,
				getComponentDefinition,
			},
			ssbm: generateBuilderManager(),
		};
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

		expect(
			mockCore.core.getComponentById(componentId).content[fieldKey],
		).toBe("new value");

		expect(vm.value).toBe("new value");
	});
});
