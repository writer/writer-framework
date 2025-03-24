import { beforeEach, describe, expect, it } from "vitest";
import BuilderFieldsHandler from "./BuilderFieldsHandler.vue";
import { flushPromises, mount } from "@vue/test-utils";
import { buildMockCore, buildMockComponent, mockProvides } from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "../builderManager";
import BuilderSelect from "../BuilderSelect.vue";
import type { generateCore } from "@/core";

describe("BuilderFieldsHandler", () => {
	let core: ReturnType<typeof generateCore>;
	let userFunctions: ReturnType<typeof buildMockCore>["userFunctions"];
	const component1 = buildMockComponent({
		id: "wf1",
		parentId: "blueprints_root",
	});
	const fieldKey = "mock-field-key";

	function buildWrapper(componentId: string) {
		const ssbm = generateBuilderManager();

		return mount(BuilderFieldsHandler, {
			props: {
				componentId,
				fieldKey,
			},
			global: {
				provide: {
					...mockProvides,
					[injectionKeys.builderManager as symbol]: ssbm,
					[injectionKeys.core as symbol]: core,
				},
			},
		});
	}

	beforeEach(() => {
		const mockCore = buildMockCore();
		core = mockCore.core;
		userFunctions = mockCore.userFunctions;
		userFunctions.value = [
			{ name: "func1", args: ["arg1", "arg2"] },
			{ name: "func2", args: ["arg1", "arg2"] },
		];

		core.addComponent(component1);
	});

	it("should initialize option", async () => {
		const wrapper = buildWrapper(component1.id);
		await flushPromises();

		expect(wrapper.attributes("data-automation-key")).toBe(fieldKey);

		const select = wrapper.getComponent(BuilderSelect);

		expect(select.props("modelValue")).toBe("");

		const options = select.props("options");
		expect(options).toHaveLength(3);
		expect(options.at(1)).toStrictEqual({
			value: "func1",
			label: "func1",
			icon: "function",
		});
	});

	it("should select an handler", async () => {
		const wrapper = buildWrapper(component1.id);
		await flushPromises();

		const select = wrapper.getComponent(BuilderSelect);

		select.vm.$emit("update:modelValue", "func1");

		await flushPromises();

		expect(core.sendComponentUpdate).toHaveBeenCalled();
		expect(select.props("modelValue")).toBe("func1");
	});

	it("should handle unexisting handler", async () => {
		const unexstingHandler = "unexsting-handler";
		const component2 = buildMockComponent({
			id: "wf3",
			parentId: "blueprints_root",
			content: { [fieldKey]: unexstingHandler },
		});
		core.addComponent(component2);

		const wrapper = buildWrapper(component2.id);
		await flushPromises();

		const select = wrapper.getComponent(BuilderSelect);

		expect(select.props("modelValue")).toBe(unexstingHandler);

		const options = select.props("options");
		expect(options).toHaveLength(4);
		expect(options.at(-1)).toStrictEqual({
			value: unexstingHandler,
			label: unexstingHandler,
		});
	});
});
