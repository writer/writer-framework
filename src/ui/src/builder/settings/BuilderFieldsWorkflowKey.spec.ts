import { beforeEach, describe, expect, it } from "vitest";
import BuilderFieldsWorkflowKey from "./BuilderFieldsWorkflowKey.vue";
import { flushPromises, mount } from "@vue/test-utils";
import { buildMockCore, buildMockComponent, mockProvides } from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "../builderManager";
import BuilderSelect from "../BuilderSelect.vue";
import WdsButton from "@/wds/WdsButton.vue";
import type { generateCore } from "@/core";

describe("BuilderFieldsWorkflowKey", () => {
	let core: ReturnType<typeof generateCore>;
	const componentWf1 = buildMockComponent({
		id: "wf1",
		type: "workflows_workflow",
		parentId: "workflows_root",
		content: { key: "wf1" },
	});
	const componentWf2 = buildMockComponent({
		id: "wf2",
		type: "workflows_workflow",
		parentId: "workflows_root",
		content: { key: "wf2" },
	});
	const fieldKey = "mock-field-key";

	function buildWrapper(componentId: string) {
		const ssbm = generateBuilderManager();

		return mount(BuilderFieldsWorkflowKey, {
			props: {
				componentId,
				fieldKey,
			},
			global: {
				stubs: {
					BaseSelect: true,
				},
				provide: {
					...mockProvides,
					[injectionKeys.builderManager as symbol]: ssbm,
					[injectionKeys.core as symbol]: core,
				},
			},
		});
	}

	beforeEach(() => {
		core = buildMockCore().core;
		core.addComponent(componentWf1);
		core.addComponent(componentWf2);
	});

	it("should initialize option", async () => {
		const wrapper = buildWrapper(componentWf2.id);
		await flushPromises();

		expect(wrapper.attributes("data-automation-key")).toBe(fieldKey);

		const select = wrapper.getComponent(BuilderSelect);

		expect(select.props("modelValue")).toBe("");

		const options = select.props("options");
		expect(options).toHaveLength(3);
		expect(options.at(1)).toStrictEqual({
			value: componentWf1.content.key,
			label: componentWf1.content.key,
			icon: "linked_services",
		});
	});

	it("should select a workflow and jump", async () => {
		const wrapper = buildWrapper(componentWf2.id);
		await flushPromises();

		const select = wrapper.getComponent(BuilderSelect);

		select.vm.$emit("update:modelValue", componentWf1.content.key);

		await flushPromises();

		expect(core.sendComponentUpdate).toHaveBeenCalled();
		expect(select.props("modelValue")).toBe(componentWf1.content.key);

		const jumpButton = wrapper.getComponent(WdsButton);

		await jumpButton.trigger("click");

		expect(core.activePageId.value).toBe(componentWf1.id);
	});

	it("should handle unexisting workflow", async () => {
		const unexstingWorkflowKey = "unexsting-workflow-key";
		const componentWf3 = buildMockComponent({
			id: "wf3",
			type: "workflows_workflow",
			parentId: "workflows_root",
			content: { key: "wf2", [fieldKey]: unexstingWorkflowKey },
		});

		core.addComponent(componentWf3);

		const wrapper = buildWrapper(componentWf3.id);
		await flushPromises();

		const select = wrapper.getComponent(BuilderSelect);

		expect(select.props("modelValue")).toBe(unexstingWorkflowKey);

		const options = select.props("options");
		expect(options).toHaveLength(4);
		expect(options.at(-1)).toStrictEqual({
			value: unexstingWorkflowKey,
			label: unexstingWorkflowKey,
		});
	});
});
