import { beforeEach, describe, expect, it, Mock, vi } from "vitest";
import { flushPromises, shallowMount } from "@vue/test-utils";
import VueDOMPurifyHTML from "vue-dompurify-html";
import BaseMarkdown from "./BaseMarkdown.vue";
import { parse, parseInline } from "marked";

vi.mock("marked", () => ({
	parse: vi.fn().mockImplementation((v) => `<div>${v}</div>`),
	parseInline: vi.fn().mockImplementation((v) => `<span>${v}</span>`),
}));

describe("BaseMarkdown", () => {
	const rawText = "# hello\nI'm **MD** ";

	beforeEach(() => {
		(parse as unknown as Mock).mockClear();
		(parseInline as unknown as Mock).mockClear();
	});

	it("should render markdown as block", async () => {
		const wrapper = shallowMount(BaseMarkdown, {
			props: { rawText },
			global: { plugins: [VueDOMPurifyHTML] },
		});
		await flushPromises();
		expect(wrapper.element).toMatchSnapshot();
		expect(parse).toHaveBeenCalledOnce();

		wrapper.setProps({ rawText: "updated" });
		await flushPromises();
		expect(parse).toHaveBeenCalledTimes(2);
	});

	it("should render markdown as inline", async () => {
		const wrapper = shallowMount(BaseMarkdown, {
			props: { rawText, inline: true },
			global: { plugins: [VueDOMPurifyHTML] },
		});
		await flushPromises();
		expect(wrapper.element).toMatchSnapshot();
		expect(parseInline).toHaveBeenCalledOnce();

		wrapper.setProps({ rawText: "updated" });
		await flushPromises();
		expect(parseInline).toHaveBeenCalledTimes(2);
	});
});
