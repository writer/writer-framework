import { flushPromises, mount, shallowMount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BuilderSelect from "./BuilderSelect.vue";
import { Option } from "./BuilderSelect.vue";
import WdsDropdownMenu from "@/wds/WdsDropdownMenu.vue";

describe("BuilderSelect", () => {
	const options: Option[] = [
		{ label: "Label A", value: "a" },
		{ label: "Label B", value: "b" },
		{ label: "Label C", value: "c" },
	];

	it("should display unknow value selected", () => {
		const wrapper = shallowMount(BuilderSelect, {
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
		const wrapper = mount(BuilderSelect, {
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

		await wrapper.get(".BuilderSelect__trigger").trigger("click");
		await flushPromises();

		const dropdownMenu = wrapper.getComponent(WdsDropdownMenu);
		dropdownMenu.vm.$emit("select", "b");
		await flushPromises();

		expect(wrapper.emitted("update:modelValue").at(0)).toStrictEqual(["b"]);
	});
});
