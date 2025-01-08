import { describe, expect, it } from "vitest";

import CoreHtml from "./CoreHtml.vue";
import { flushPromises, mount } from "@vue/test-utils";
import injectionKeys from "@/injectionKeys";
import { ref } from "vue";
import { mockProvides } from "@/tests/mocks";

describe("CoreCheckboxInput", () => {
	it("should filter invalid Attributes props", async () => {
		const wrapper = mount(CoreHtml, {
			slots: {
				default: "slot",
			},
			global: {
				provide: {
					...mockProvides,
					[injectionKeys.evaluatedFields as symbol]: {
						htmlInside: ref("inside"),
						element: ref("div"),
						styles: ref({
							color: "red",
						}),
						attrs: ref({
							"0invalid": "invalid",
							valid: "valid",
						}),
					},
				},
			},
		});

		await flushPromises();

		const attrs = wrapper.attributes();

		expect(attrs.valid).toBe("valid");
		expect(attrs.invalid).toBeUndefined();
		expect(attrs.style).toBe("color: red;");

		expect(wrapper.element).toMatchSnapshot();
	});
});
