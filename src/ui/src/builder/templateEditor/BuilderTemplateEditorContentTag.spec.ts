import { describe, it, expect } from "vitest";

import BuilderTemplateEditorContentTag from "./BuilderTemplateEditorContentTag.vue";
import { shallowMount } from "@vue/test-utils";

describe(BuilderTemplateEditorContentTag, () => {
	it("should display basic", () => {
		const wrapper = shallowMount(BuilderTemplateEditorContentTag, {
			props: {
				backgroundColors: {
					red: ["foo"],
				},
				tag: "foo",
			},
		});
		expect(wrapper.element.style.backgroundColor).toBe("red");
	});

	it("should handle nested", () => {
		const wrapper = shallowMount(BuilderTemplateEditorContentTag, {
			props: {
				backgroundColors: {
					red: ["foo"],
				},
				tag: "foo.bar",
			},
		});
		expect(wrapper.element.style.backgroundColor).toBe("red");
	});

	it("should handle no match", () => {
		const wrapper = shallowMount(BuilderTemplateEditorContentTag, {
			props: {
				backgroundColors: {
					red: ["foo"],
				},
				tag: "bar.foo",
			},
		});
		expect(wrapper.element.style.backgroundColor).toBe("");
	});
});
