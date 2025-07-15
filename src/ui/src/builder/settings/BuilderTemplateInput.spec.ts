import { describe, it, expect, vi } from "vitest";
import { flushPromises, shallowMount } from "@vue/test-utils";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import BuilderStateSelectorDropdown from "../stateDropdown/BuilderStateSelectorDropdown.vue";
import BuilderTemplateInputTemplate from "./BuilderTemplateInputTemplate.vue";

describe("BuilderTemplateInput", () => {
	it.each(["@", "@{"])('should autocomplete with "%s"', async (value) => {
		const getSelection = vi.fn().mockReturnValue({
			selectionEnd: value.length,
			selectionStart: value.length,
		});
		const focus = vi.fn();
		const setSelectionStart = vi.fn();
		const setSelectionEnd = vi.fn();
		const wrapper = shallowMount(BuilderTemplateInput, {
			global: {
				stubs: {
					BuilderTemplateInputTemplate: {
						template: `<div></div>`,
						setup() {
							return {
								getSelection,
								focus,
								setSelectionStart,
								setSelectionEnd,
							};
						},
					},
				},
			},
		});

		const input = wrapper.getComponent(BuilderTemplateInputTemplate);

		input.vm.value = value;
		input.vm.$emit("input", { target: { value } });

		await flushPromises();

		const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
		expect(dropdown.props("query")).toBe("");

		dropdown.vm.$emit("update:modelValue", "text");

		await flushPromises();

		expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
			"@{text}",
		]);
	});

	it("should autocomplete with templating", async () => {
		const value = "foo @{tex";
		const getSelection = vi.fn().mockReturnValue({
			selectionEnd: value.length,
			selectionStart: value.length,
		});
		const focus = vi.fn();
		const setSelectionStart = vi.fn();
		const setSelectionEnd = vi.fn();
		const wrapper = shallowMount(BuilderTemplateInput, {
			global: {
				stubs: {
					BuilderTemplateInputTemplate: {
						template: `<div></div>`,
						setup() {
							return {
								getSelection,
								focus,
								setSelectionStart,
								setSelectionEnd,
							};
						},
					},
				},
			},
		});

		const input = wrapper.getComponent(BuilderTemplateInputTemplate);

		input.vm.value = value;
		input.vm.$emit("input", { target: { value } });

		await flushPromises();

		const dropdown = wrapper.getComponent(BuilderStateSelectorDropdown);
		expect(dropdown.props("query")).toBe("tex");

		dropdown.vm.$emit("update:modelValue", "text");

		await flushPromises();

		expect(wrapper.emitted("update:value").at(-1)).toStrictEqual([
			"foo @{text}",
		]);
	});
});
