import { describe, expect, it } from "vitest";
import BaseMarkdownRaw from "../base/BaseMarkdownRaw.vue";
import CoreAnnotatedText from "./CoreAnnotatedText.vue";
import VueDOMPurifyHTML from "vue-dompurify-html";
import injectionKeys from "@/injectionKeys";
import { buildMockCore, mockProvides } from "@/tests/mocks";
import { flushPromises, shallowMount } from "@vue/test-utils";
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

		const wrapper = shallowMount(CoreAnnotatedText, {
			global: {
				plugins: [VueDOMPurifyHTML],
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.isBeingEdited as symbol]: ref(false),
					[injectionKeys.evaluatedFields as symbol]: {
						text: ref(text),
						seed: ref(1),
						useMarkdown: ref("no"),
						rotateHue: ref("yes"),
						referenceColor: ref(WdsColor.Blue5),
						copyButtons: ref("yes"),
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
		expect(annotations.at(1).attributes().style).toMatchInlineSnapshot(
			`"background-color: rgb(180, 237, 238);"`,
		);

		expect(wrapper.element).toMatchSnapshot();
	});

	it("should render in markdown mode", async () => {
		const { core } = buildMockCore();

		const wrapper = shallowMount(CoreAnnotatedText, {
			global: {
				plugins: [VueDOMPurifyHTML],
				provide: {
					...mockProvides,
					[injectionKeys.core as symbol]: core,
					[injectionKeys.isBeingEdited as symbol]: ref(false),
					[injectionKeys.evaluatedFields as symbol]: {
						text: ref(text),
						seed: ref(1),
						useMarkdown: ref("yes"),
						rotateHue: ref("yes"),
						referenceColor: ref(WdsColor.Blue5),
						copyButtons: ref("yes"),
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
