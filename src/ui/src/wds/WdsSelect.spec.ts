import { flushPromises, mount, shallowMount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import WdsSelect from "./WdsSelect.vue";
import { Option } from "./WdsSelect.vue";
import WdsDropdownMenu from "@/wds/WdsDropdownMenu.vue";

describe("WdsSelect", () => {
	const options: Option[] = [
		{ label: "Label A", value: "a" },
		{ label: "Label B", value: "b" },
		{ label: "Label C", value: "c" },
	];

	it("should display unknow value selected", () => {
		const wrapper = shallowMount(WdsSelect, {
			props: {
				modelValue: "x",
				enableMultiSelection: false,
				hideIcons: true,
				options,
			},
		});

		expect(wrapper.get(".material-symbols-outlined").text()).toBe(
			"help_center",
		);
	});

	it("should support single mode", async () => {
		const wrapper = mount(WdsSelect, {
			props: {
				modelValue: "a",
				enableMultiSelection: false,
				options,
			},
			global: {
				stubs: {
					WdsDropdownMenu: true,
				},
			},
		});
		await flushPromises();

		await wrapper.get(".WdsSelect__trigger").trigger("click");
		await flushPromises();

		const dropdownMenu = wrapper.getComponent(WdsDropdownMenu);
		dropdownMenu.vm.$emit("select", "b");
		await flushPromises();

		expect(wrapper.emitted("update:modelValue").at(0)).toStrictEqual(["b"]);
	});
});
