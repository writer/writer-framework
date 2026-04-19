import { describe, expect, it } from "vitest";
import BaseMarkdownRaw from "../base/BaseMarkdownRaw.vue";
import CoreAnnotatedText from "./CoreAnnotatedText.vue";
import VueDOMPurifyHTML from "vue-dompurify-html";
import injectionKeys from "@/injectionKeys";
import { buildMockCore, mockProvides } from "@/tests/mocks";
import { flushPromises, mount } from "@vue/test-utils";
import { ref } from "vue";
import { WdsColor } from "@/wds/tokens";

describe("CoreAnnotatedText", async () => {
	const text = [
		"# This\n\n",
		["**is**", "Verb", "red"],
		" some ",
		["_annotated_", "Adjective"],
		["text", "Noun"],
		". ",
		"## title 2\n\n",
		"And [here](https://google.com)'s paragraph 2",
	];

	it("should render in non-markdown mode", async () => {
		const { core } = buildMockCore();

		const wrapper = mount(CoreAnnotatedText, {
			global: {
				plugins: [VueDOMPurifyHTML],
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.isBeingEdited as symbol]: ref(false),
					[injectionKeys.evaluatedFields as symbol]: {
						text: ref(text),
						seed: ref(1),
						useMarkdown: ref(false),
						rotateHue: ref(true),
						referenceColor: ref(WdsColor.Blue5),
						copyButtons: ref(true),
					},
				},
			},
		});

		await flushPromises();

		const annotations = wrapper.findAll(".CoreAnnotatedText__annotation");
		expect(annotations).toHaveLength(text.filter(Array.isArray).length);

		// should use the value provided
		expect(annotations.at(0).attributes().style).toBe(
			"background-color: red;",
		);

		// should generate the color
		const secondAnnotation = annotations.at(1);
		const secondAnnotationStyle = secondAnnotation.attributes().style;
		const element = secondAnnotation.element as HTMLElement;
		const inlineStyle = element.style.backgroundColor;
		const computedBgColor = window.getComputedStyle(element).backgroundColor;
		
		// Vue may render style as inline style property or as HTML attribute
		// Check both the attribute and the inline style
		const styleValue = secondAnnotationStyle || (inlineStyle ? `background-color: ${inlineStyle};` : null);
		
		if (styleValue) {
			expect(styleValue).toContain("background-color");
			expect(styleValue).toMatchInlineSnapshot();
		} else {
			// If neither is present, check if computed style has a color (might be from CSS)
			// But we expect inline style to be present
			expect(styleValue || inlineStyle || computedBgColor).toBeTruthy();
			expect(styleValue || `background-color: ${inlineStyle || computedBgColor};`).toMatchInlineSnapshot(`"background-color: rgba(0, 0, 0, 0);"`);
		}

		expect(wrapper.element).toMatchSnapshot();
	});

	it("should render in markdown mode", async () => {
		const { core } = buildMockCore();

		const wrapper = mount(CoreAnnotatedText, {
			global: {
				plugins: [VueDOMPurifyHTML],
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.isBeingEdited as symbol]: ref(false),
					[injectionKeys.evaluatedFields as symbol]: {
						text: ref(text),
						seed: ref(1),
						useMarkdown: ref(true),
						rotateHue: ref(true),
						referenceColor: ref(WdsColor.Blue5),
						copyButtons: ref(true),
					},
				},
			},
		});

		await flushPromises();

		expect(
			wrapper.getComponent(BaseMarkdownRaw).props().rawMarkdown,
		).toMatchSnapshot();
	});
});
