import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StateWithPills from "./StateWithPills.vue";
import StateWithPillsTag from "./StateWithPillsTag.vue";

describe("StateWithPills", () => {
	it("should render simple text", () => {
		const content = "hello";
		const wrapper = mount(StateWithPills, {
			props: { content },
		});
		const tags = wrapper.findAll(".StateWithPill__tag");
		expect(tags).toHaveLength(0);
		expect(wrapper.text()).toBe(content);
	});

	it("should render text with one tag", () => {
		const content = "hello @{tag}";
		const wrapper = mount(StateWithPills, {
			props: { content },
		});
		const tags = wrapper.findAllComponents(StateWithPillsTag);
		expect(tags).toHaveLength(1);
		expect(tags.at(0).text()).toBe("@{tag}");

		expect(wrapper.text()).toBe(content);
	});

	it("should render text with breaking lines", () => {
		const content = "hello @{tag}\nand ${tag}";
		const wrapper = mount(StateWithPills, {
			props: { content },
		});
		const tags = wrapper.findAll("br");
		expect(tags).toHaveLength(1);
	});
});
