import { describe, expect, it, vi } from "vitest";

import CoreRadioInput from "./CoreRadioInput.vue";
import { flushPromises, mount } from "@vue/test-utils";
import injectionKeys from "@/injectionKeys";
import { ref } from "vue";
import { buildMockComponent, buildMockCore, mockProvides } from "@/tests/mocks";

describe("CoreRadioInput", () => {
	it("should render value from the state and forward emit", async () => {
		const { core, userState } = buildMockCore();
		userState.value = { key: "b" };

		core.addComponent(
			buildMockComponent({
				handlers: { "wf-option-change": "python_handler" },
				binding: {
					eventType: "",
					stateRef: "key",
				},
			}),
		);

		const wrapper = mount(CoreRadioInput, {
			global: {
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.evaluatedFields as symbol]: {
						label: ref("This is the label"),
						orientation: ref("horizontal"),
						options: ref({ a: "Option A", b: "Option B" }),
					},
				},
			},
		});

		await flushPromises();

		const options = wrapper.findAll("input");
		expect(options).toHaveLength(2);

		const optionA = options.at(0);
		expect(optionA.attributes().value).toBe("a");
		expect(optionA.element.checked).toBe(false);

		const optionB = options.at(1);
		expect(optionB.attributes().value).toBe("b");
		expect(optionB.element.checked).toBe(true);

		const dispatchEvent = vi.spyOn(wrapper.vm.$el, "dispatchEvent");
		await optionA.trigger("input");
		await flushPromises();
		expect(dispatchEvent).toHaveBeenCalledOnce();

		expect(wrapper.element).toMatchSnapshot();
	});
});
