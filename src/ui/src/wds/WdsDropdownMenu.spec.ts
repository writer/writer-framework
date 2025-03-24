import { shallowMount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import WdsDropdownMenu from "./WdsDropdownMenu.vue";
import { WdsDropdownMenuOption } from "./WdsDropdownMenu.vue";
import WdsCheckbox from "./WdsCheckbox.vue";

describe("WdsDropdownMenu", () => {
	const options: WdsDropdownMenuOption[] = [
		{ label: "Label A", value: "a" },
		{ label: "Label B", value: "b" },
		{ label: "Label C", value: "c" },
	];

	describe("single mode", () => {
		it("should select an option", async () => {
			const wrapper = shallowMount(WdsDropdownMenu, {
				props: {
					selected: "a",
					enableMultiSelection: false,
					options,
				},
			});

			await wrapper
				.get(`.WdsDropdownMenu__item[data-automation-key="b"]`)
				.trigger("click");

			expect(wrapper.emitted("select").at(0)).toStrictEqual(["b"]);
		});
	});

	describe("multiple mode", () => {
		it("should support multiple mode", () => {
			const wrapper = shallowMount(WdsDropdownMenu, {
				props: {
					selected: ["???"],
					enableMultiSelection: true,
					options,
				},
			});

			wrapper.getComponent(WdsCheckbox).vm.$emit("update:modelValue");

			expect(wrapper.emitted("select").at(0)).toStrictEqual([["a"]]);
		});
	});
});
