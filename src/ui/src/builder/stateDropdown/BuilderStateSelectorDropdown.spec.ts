import { beforeEach, describe, it, expect } from "vitest";
import BuilderStateSelectorDropdown from "./BuilderStateSelectorDropdown.vue";
import {
	buildMockComponent,
	buildMockCore,
	buildMockSecretsManager,
} from "@/tests/mocks";
import { Component } from "@/writerTypes";
import { flushPromises, mount } from "@vue/test-utils";
import injectionKeys from "@/injectionKeys";
import { generateBuilderManager } from "../builderManager";
import { ExtractPropTypes } from "vue";
import WdsDropdownMenuItem from "@/wds/WdsDropdownMenuItem.vue";

describe("BuilderStateSelectorDropdown", () => {
	let mockCore: ReturnType<typeof buildMockCore>;
	let mockSecretsManager: ReturnType<typeof buildMockSecretsManager>;

	const baseComponent: Pick<Component, "id" | "type" | "parentId"> = {
		id: "c1",
		parentId: "blueprints_root",
		type: "blueprints_setstate",
	};

	beforeEach(() => {
		mockCore = buildMockCore();
		mockSecretsManager = buildMockSecretsManager(mockCore.core);
	});

	function mountBuilderStateSelectorDropdown(
		props: ExtractPropTypes<typeof BuilderStateSelectorDropdown> = {},
	) {
		return mount(BuilderStateSelectorDropdown, {
			global: {
				stubs: {
					SharedImgWithFallback: true,
				},
				provide: {
					[injectionKeys.core]: mockCore.core,
					[injectionKeys.secretsManager]:
						mockSecretsManager.secretsManager,
					[injectionKeys.builderManager]: generateBuilderManager(),
				},
			},
			props,
		});
	}

	it("should get option from initial state", async () => {
		mockCore.userStateInitial.value = { foo: { bar: 1 } };
		const wrapper = mountBuilderStateSelectorDropdown();

		await wrapper.get('[data-automation-key="foo.bar"]').trigger("click");

		expect(wrapper.emitted("update:modelValue")).toStrictEqual([
			["foo.bar"],
		]);
	});

	it("should get option from binding", async () => {
		const component = buildMockComponent({
			...baseComponent,
			binding: {
				stateRef: "foo.bar",
				eventType: "wf-change",
			},
		});
		mockCore.core.addComponent(component);
		const wrapper = mountBuilderStateSelectorDropdown();

		await wrapper.get('[data-automation-key="foo.bar"]').trigger("click");

		expect(wrapper.emitted("update:modelValue")).toStrictEqual([
			["foo.bar"],
		]);
	});

	it("should get option from set state", async () => {
		const component = buildMockComponent({
			...baseComponent,
			content: {
				element: "foo.bar",
				valueType: "JSON",
				value: JSON.stringify({ bar: "baz" }),
			},
		});
		mockCore.core.addComponent(component);
		const wrapper = mountBuilderStateSelectorDropdown();

		await wrapper.get('[data-automation-key="foo.bar"]').trigger("click");

		expect(wrapper.emitted("update:modelValue")).toStrictEqual([
			["foo.bar"],
		]);
	});

	it("should search from the options", async () => {
		mockCore.userStateInitial.value = {
			state: "azerty",
		};
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				id: "c1",
				content: {
					element: "setState",
					valueType: "JSON",
					value: JSON.stringify({ bar: "baz" }),
				},
			}),
		);
		mockCore.core.addComponent(
			buildMockComponent({
				...baseComponent,
				id: "c2",
				binding: {
					stateRef: "binding",
					eventType: "wf-change",
				},
			}),
		);
		mockSecretsManager.secrets.value = {
			apiKey: "A",
		};

		const wrapper = mountBuilderStateSelectorDropdown();

		expect(wrapper.element).toMatchSnapshot();

		expect(wrapper.findAllComponents(WdsDropdownMenuItem)).toHaveLength(4);

		wrapper.setProps({ query: "api" });
		await flushPromises();

		expect(wrapper.findAllComponents(WdsDropdownMenuItem)).toHaveLength(1);
	});

	it("should be able to add", async () => {
		const wrapper = mountBuilderStateSelectorDropdown({
			query: "azerty",
			allowCreate: true,
		});

		expect(wrapper.findAllComponents(WdsDropdownMenuItem)).toHaveLength(1);

		await wrapper.get('[data-automation-key="azerty"]').trigger("click");
		await flushPromises();

		expect(wrapper.emitted("update:modelValue")).toStrictEqual([
			["azerty"],
		]);
	});

	it("should display empty message", async () => {
		const wrapper = mountBuilderStateSelectorDropdown({
			query: "azerty",
			allowCreate: false,
		});

		expect(wrapper.findAllComponents(WdsDropdownMenuItem)).toHaveLength(0);

		expect(
			wrapper.find(".BuilderStateSelectorDropdown__empty").exists(),
		).toBe(true);
	});
});
