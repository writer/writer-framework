import { describe, expect, it, vi } from "vitest";

import CoreDateInput from "./CoreDateInput.vue";
import { flushPromises, mount } from "@vue/test-utils";
import injectionKeys from "@/injectionKeys";
import { ref } from "vue";
import { buildMockComponent, buildMockCore, mockProvides } from "@/tests/mocks";

describe("CoreDateInput", () => {
	it("should render value from the state and forward emit", async () => {
		const { core, userState } = buildMockCore();
		userState.value = { key: "2024-12-14" };
		core.addComponent(
			buildMockComponent({
				handlers: { "wf-date-change": "python_handler" },
				binding: {
					eventType: "",
					stateRef: "key",
				},
			}),
		);

		const wrapper = mount(CoreDateInput, {
			global: {
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.evaluatedFields as symbol]: {
						label: ref("This is the label"),
					},
				},
			},
		});

		await flushPromises();

		const input = wrapper.get("input");
		expect(input.element.value).toStrictEqual("2024-12-14");

		const dispatchEvent = vi.spyOn(wrapper.vm.$el, "dispatchEvent");

		await input.trigger("change");

		await flushPromises();

		expect(dispatchEvent).toHaveBeenCalledOnce();

		expect(wrapper.element).toMatchSnapshot();
	});
});
