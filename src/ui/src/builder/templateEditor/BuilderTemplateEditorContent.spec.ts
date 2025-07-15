import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import BuilderTemplateEditorContent from "./BuilderTemplateEditorContent.vue";
import BuilderTemplateEditorContentTag from "./BuilderTemplateEditorContentTag.vue";

describe("BuilderTemplateEditorContent", () => {
	it("should render simple text", () => {
		const content = "hello";
		const wrapper = mount(BuilderTemplateEditorContent, {
			props: { content },
		});
		const tags = wrapper.findAll(".BuilderTemplateEditorContent__tag");
		expect(tags).toHaveLength(0);
		expect(wrapper.text()).toBe(content);
		expect(wrapper.element).toMatchSnapshot();
	});

	it("should render text with one tag", () => {
		const content = "hello @{tag}";
		const wrapper = mount(BuilderTemplateEditorContent, {
			props: { content },
		});
		const tags = wrapper.findAllComponents(BuilderTemplateEditorContentTag);
		expect(tags).toHaveLength(1);
		expect(tags.at(0).text()).toBe("@{tag}");

		expect(wrapper.text()).toBe(content);
		expect(wrapper.element).toMatchSnapshot();
	});

	it("should render text with breaking lines", () => {
		const content = "hello @{tag}\nand ${tag}";
		const wrapper = mount(BuilderTemplateEditorContent, {
			props: { content },
		});
		const tags = wrapper.findAll("br");
		expect(tags).toHaveLength(1);
		expect(wrapper.element).toMatchSnapshot();
	});
});
