import { describe, expect, it } from "vitest";

import CoreButton from "./CoreButton.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { shallowMount } from "@vue/test-utils";
import injectionKeys from "@/injectionKeys";
import { ref } from "vue";
import { mockProvides } from "@/tests/mocks";

describe("CoreButton", () => {
	describe("isDisabled", () => {
		it("should disable the button in preview mode", () => {
			const wrapper = shallowMount(CoreButton, {
				slots: {
					default: "slot",
				},
				global: {
					provide: {
						...mockProvides,
						[injectionKeys.isBeingEdited as symbol]: false,
						[injectionKeys.isDisabled as symbol]: ref(false),
						[injectionKeys.evaluatedFields as symbol]: {
							isDisabled: ref(true),
							text: ref("hello"),
						},
					},
				},
			});

			const button = wrapper.getComponent(WdsButton);

			expect(button.attributes()).toStrictEqual(
				expect.objectContaining({
					disabled: "true",
					"aria-disabled": "true",
				}),
			);
		});

		it("should not disable the button in edit mode", () => {
			const wrapper = shallowMount(CoreButton, {
				slots: {
					default: "slot",
				},
				global: {
					provide: {
						...mockProvides,
						[injectionKeys.isBeingEdited as symbol]: true,
						[injectionKeys.isDisabled as symbol]: ref(false),
						[injectionKeys.evaluatedFields as symbol]: {
							isDisabled: ref(true),
							text: ref("hello"),
						},
					},
				},
			});

			const button = wrapper.getComponent(WdsButton);

			expect(button.attributes()).toStrictEqual(
				expect.objectContaining({
					disabled: "false",
					"aria-disabled": "true",
				}),
			);
		});
	});
});
