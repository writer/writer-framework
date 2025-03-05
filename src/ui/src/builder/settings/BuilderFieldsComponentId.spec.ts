import { beforeEach, describe, expect, it } from "vitest";
import BuilderFieldsComponentId from "./BuilderFieldsComponentId.vue";
import { flushPromises, mount } from "@vue/test-utils";
import { buildMockCore, buildMockComponent, mockProvides } from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "../builderManager";
import BuilderSelect from "../BuilderSelect.vue";
import WdsButton from "@/wds/WdsButton.vue";
import type { generateCore } from "@/core";

describe("BuilderFieldsComponentId", () => {
	let core: ReturnType<typeof generateCore>;
	let wfbm: ReturnType<typeof generateBuilderManager>;
	const componentPage = buildMockComponent({
		id: "page-1",
		type: "page",
		parentId: "root",
	});
	const componentButton = buildMockComponent({
		id: "button-1",
		type: "button",
		content: {
			text: "I am a button",
		},
		parentId: componentPage.id,
	});
	const fieldKey = "mock-field-key";

	function buildWrapper(componentId: string) {
		return mount(BuilderFieldsComponentId, {
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
					[injectionKeys.builderManager as symbol]: wfbm,
					[injectionKeys.core as symbol]: core,
				},
			},
		});
	}

	beforeEach(() => {
		core = buildMockCore().core;
		core.addComponent(componentButton);
		core.addComponent(componentPage);

		wfbm = generateBuilderManager();
	});

	it("should initialize option", async () => {
		const wrapper = buildWrapper(componentPage.id);
		await flushPromises();

		expect(wrapper.attributes("data-automation-key")).toBe(fieldKey);

		const select = wrapper.getComponent(BuilderSelect);

		expect(select.props("modelValue")).toBe("");

		const options = select.props("options");
		expect(options).toHaveLength(2);
		expect(options.at(1)).toStrictEqual({
			value: componentButton.id,
			label: componentButton.content.text,
			detail: "Button",
			icon: [
				"http://localhost:3000/components/button.svg",
				"http://localhost:3000/components/category_Other.svg",
			],
		});
	});

	it("should select a component and jump", async () => {
		const wrapper = buildWrapper(componentPage.id);
		await flushPromises();

		const select = wrapper.getComponent(BuilderSelect);

		select.vm.$emit("update:modelValue", componentButton.id);

		await flushPromises();

		expect(core.sendComponentUpdate).toHaveBeenCalled();
		expect(select.props("modelValue")).toBe(componentButton.id);

		const jumpButton = wrapper.getComponent(WdsButton);

		await jumpButton.trigger("click");

		expect(core.activePageId.value).toBe(componentPage.id);
		expect(wfbm.firstSelectedId.value).toBe(componentButton.id);
	});
});
