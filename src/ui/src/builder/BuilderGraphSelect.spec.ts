import { beforeEach, describe, expect, it, vi } from "vitest";
import BuilderGraphSelect from "./BuilderGraphSelect.vue";
import { flushPromises, shallowMount } from "@vue/test-utils";
import { buildMockCore } from "@/tests/mocks";
import injectionKeys from "@/injectionKeys";
import BuilderSelect from "./BuilderSelect.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";

describe("BuilderGraphSelect", () => {
	const graphs = [
		{ id: "1", name: "one" },
		{ id: "2", name: "two" },
	];
	let core: ReturnType<typeof buildMockCore>["core"];

	beforeEach(() => {
		core = buildMockCore().core;
	});

	it("should fetch and display graphs", async () => {
		const sendListResourcesRequest = vi
			.spyOn(core, "sendListResourcesRequest")
			.mockResolvedValue(graphs);

		const wrapper = shallowMount(BuilderGraphSelect, {
			props: { modelValue: "1" },
			global: {
				stubs: {
					BuilderSelect: true,
				},
				provide: {
					[injectionKeys.core as symbol]: core,
				},
			},
		});
		await flushPromises();
		expect(sendListResourcesRequest).toHaveBeenCalledOnce();
		expect(wrapper.findComponent(BuilderSelect).exists()).toBe(true);
	});

	it("should fallback to input", async () => {
		const sendListResourcesRequest = vi
			.spyOn(core, "sendListResourcesRequest")
			.mockRejectedValue(new Error());

		const wrapper = shallowMount(BuilderGraphSelect, {
			props: { modelValue: "1" },
			global: {
				stubs: {
					BuilderSelect: true,
				},
				provide: {
					[injectionKeys.core as symbol]: core,
				},
			},
		});
		await flushPromises();
		expect(sendListResourcesRequest).toHaveBeenCalledOnce();
		expect(wrapper.findComponent(BuilderSelect).exists()).toBe(false);
		expect(wrapper.findComponent(WdsTextInput).exists()).toBe(true);
	});
});
