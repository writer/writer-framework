import { describe, expect, it, beforeEach, beforeAll } from "vitest";
import BaseMarkdown from "../base/BaseMarkdown.vue";
import CoreText from "./CoreText.vue";
import injectionKeys from "@/injectionKeys";
import { buildMockComponent, buildMockCore, mockProvides } from "@/tests/mocks";
import { shallowMount } from "@vue/test-utils";
import { ref } from "vue";
import { Core } from "@/writerTypes";

describe("CoreText", async () => {
	const text = `# Hello\n\nI'm the **content**.`;
	let core: Core;

	beforeAll(() => {
		core = buildMockCore().core;

		core.addComponent(
			buildMockComponent({
				handlers: { "wf-click": "python_handler" },
			}),
		);
	});

	it("should render in non-markdown mode", () => {
		const wrapper = shallowMount(CoreText, {
			global: {
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.isBeingEdited as symbol]: ref(false),
					[injectionKeys.evaluatedFields as symbol]: {
						text: ref(text),
						alignment: ref("center"),
						useMarkdown: ref(false),
					},
				},
			},
		});

		expect(wrapper.element).toMatchSnapshot();
	});

	it("should render in markdown mode", () => {
		const wrapper = shallowMount(CoreText, {
			global: {
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.isBeingEdited as symbol]: ref(false),
					[injectionKeys.evaluatedFields as symbol]: {
						text: ref(text),
						alignment: ref("center"),
						useMarkdown: ref(true),
					},
				},
			},
		});

		expect(wrapper.findComponent(BaseMarkdown).exists()).toBe(true);

		expect(wrapper.element).toMatchSnapshot();
	});
});
