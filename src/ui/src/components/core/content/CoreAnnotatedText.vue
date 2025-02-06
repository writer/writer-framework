<template>
	<div v-if="shouldDisplay" class="CoreAnnotatedText">
		<BaseMarkdownRaw
			v-if="useMarkdown"
			:raw-markdown="markdown"
			class="CoreAnnotatedText__markdown"
		/>
		<template v-else>
			<BaseEmptiness v-if="isEmpty" :component-id="componentId" />
			<span v-for="(content, i) in text" :key="String(content) + i">
				<template v-if="typeof content === 'string'">{{
					content
				}}</template>
				<span
					v-if="Array.isArray(content)"
					class="CoreAnnotatedText__annotation"
					:style="{ backgroundColor: getAnnotationBgColor(content) }"
				>
					{{ content[0] }}
					<span
						v-if="content[1]"
						class="CoreAnnotatedText__annotation__subject"
					>
						{{ content[1] }}
					</span>
				</span>
			</span>
		</template>
		<SharedControlBar
			v-if="fields.copyButtons.value === 'yes'"
			:copy-raw-content="copyRawContent"
			:copy-structured-content="copyStructuredContent"
		/>
	</div>
</template>

<script lang="ts">
import {
	buttonColor,
	buttonTextColor,
	cssClasses,
	primaryTextColor,
} from "@/renderer/sharedStyleFields";
import SharedControlBar from "@/components/shared/SharedControlBar.vue";
import { WdsColor } from "@/wds/tokens";
import { validatorAnotatedText } from "@/constants/validators";
export default {
	writer: {
		name: "Annotated text",
		description: "Shows text with annotations",
		category: "Content",
		fields: {
			text: {
				name: "Annotated text",
				type: FieldType.Object,
				desc: "Value array with text/annotations. Must be a JSON string or a state reference to an array.",
				init: `["This ",["is", "Verb"]," some ",["annotated", "Adjective"], ["text", "Noun"]," for those of ",["you", "Pronoun"]," who ",["like", "Verb"]," this sort of ",["thing", "Noun"],". ","And here's a ",["word", "", "#faf"]," with a fancy background but no label."]`,
				validator: validatorAnotatedText,
			},
			referenceColor: {
				name: "Reference",
				desc: "The colour to be used as reference for chroma and luminance, and as the starting point for hue rotation.",
				type: FieldType.Color,
				default: WdsColor.Blue5,
				category: FieldCategory.Style,
			},
			seed: {
				name: "Seed value",
				desc: "Choose a different value to reshuffle colours.",
				type: FieldType.Number,
				default: "1",
				category: FieldCategory.Style,
			},
			rotateHue: {
				name: "Rotate hue",
				desc: "If active, rotates the hue depending on the content of the string. If turned off, the reference colour is always used.",
				type: FieldType.Text,
				options: {
					yes: "yes",
					no: "no",
				},
				default: "yes",
				category: FieldCategory.Style,
			},
			useMarkdown: {
				name: "Use Markdown",
				desc: "If active, the output will be sanitized; unsafe elements will be removed.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			copyButtons: {
				name: "Copy buttons",
				desc: "If active, adds a control bar with both copy text and JSON buttons.",
				type: FieldType.Text,
				options: {
					yes: "yes",
					no: "no",
				},
				default: "no",
				category: FieldCategory.Style,
			},
			buttonColor,
			buttonTextColor,
			primaryTextColor,
			cssClasses,
		},
		previewField: "data",
	},
};
</script>
<script setup lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { computed, inject, readonly, ref, watch } from "vue";
import chroma, { Color } from "chroma-js";
import { useFieldValueAsYesNo } from "@/composables/useFieldValue";
import BaseEmptiness from "../base/BaseEmptiness.vue";
import BaseMarkdownRaw from "../base/BaseMarkdownRaw.vue";

type AnnotatedTextElementArray = [content: string, tag: string, color?: string];
type AnnotatedTextElement = string | AnnotatedTextElementArray;

const fields = inject(injectionKeys.evaluatedFields);

const text = computed<AnnotatedTextElement[]>(() => fields.text.value ?? []);

const isBeingEdited = inject(injectionKeys.isBeingEdited);
const componentId = inject(injectionKeys.componentId);
const isEmpty = computed(() => !fields.text.value);
const shouldDisplay = computed(() => !isEmpty.value || isBeingEdited.value);
const useMarkdown = useFieldValueAsYesNo(fields, "useMarkdown");

const COLOR_STEPS = [
	{ h: -78, s: -34, l: 16 },
	{ h: -61, s: -37, l: 16 },
	{ h: -2, s: 0, l: 24 },
	{ h: -12, s: 0, l: 29 },
	{ h: 28, s: -20, l: 24 },
	{ h: -61, s: -95, l: 25 },
	{ h: -173, s: 0, l: 16 },
	{ h: -228, s: 0, l: 22 },
	{ h: 69, s: 0, l: 25 },
	{ h: 70, s: 0, l: 29 },
];

let currentSteps = [...COLOR_STEPS];
let subjectColorCache = {};
let lastSeed = fields.seed.value;

function useMarkdownRenderer() {
	const markdown = ref("");

	watch(
		[useMarkdown, text],
		async () => {
			if (!useMarkdown.value) return (markdown.value = "");
			markdown.value = await parseMarkdown();
		},
		{ immediate: true },
	);

	/* Translate annotation as `<span>` to use it inside the markdown */
	function RawAnnotation(element: AnnotatedTextElementArray) {
		const [content, subject] = element;
		const subjectEl = subject
			? `<span class="CoreAnnotatedText__annotation__subject">${subject}</span>`
			: "";

		return `<span class="CoreAnnotatedText__annotation" style="background: ${getAnnotationBgColor(element)}">${content}${subjectEl}</span>`;
	}

	async function parseMarkdown() {
		const rawMarkdown = text.value.reduce<string>((acc, part) => {
			if (typeof part === "string") {
				return `${acc} ${part}`;
			} else if (Array.isArray(part)) {
				return `${acc} ${RawAnnotation(part)}`;
			} else {
				return acc;
			}
		}, "");

		const marked = await import("marked");
		return await marked.parse(rawMarkdown);
	}

	return readonly(markdown);
}

const markdown = useMarkdownRenderer();

function generateColorCss(
	baseColor: Color,
	colorData: { h: number; s: number; l: number },
) {
	let genColor = baseColor
		.set(
			"hsl.h",
			`${Math.sign(colorData.h) == -1 ? "-" : "+"}${Math.abs(colorData.h)}`,
		)
		.set(
			"hsl.s",
			`${Math.sign(colorData.s) == -1 ? "-" : "+"}${Math.abs(colorData.s / 100.0)}`,
		)
		.set(
			"hsl.l",
			`${Math.sign(colorData.l) == -1 ? "-" : "+"}${Math.abs(colorData.l / 100.0)}`,
		);

	return genColor.css();
}

function calculateColorStep(s: string, stepsLength = COLOR_STEPS.length) {
	let hash = (fields.seed.value * 52673) & 0xffffffff;
	for (let i = 0; i < s.length; i++) {
		hash = ((i + 1) * s.charCodeAt(i)) ^ (hash & 0xffffffff);
	}
	const step = Math.abs(hash) % stepsLength;

	return step;
}

function getAnnotationBgColor(content: AnnotatedTextElementArray) {
	return content[2] || generateColor(content[1]);
}

function generateColor(s: string) {
	if (fields.rotateHue.value == "no") {
		return fields.referenceColor.value;
	}

	const baseColor = chroma(fields.referenceColor.value);

	if (lastSeed !== fields.seed.value) {
		currentSteps = [...COLOR_STEPS];
		subjectColorCache = {};
		lastSeed = fields.seed.value;
	}

	if (subjectColorCache[s]) {
		return generateColorCss(baseColor, subjectColorCache[s]);
	}

	// If we run out of colors, reset the list
	if (currentSteps.length === 0) {
		currentSteps = [...COLOR_STEPS];
	}

	const colorStep = calculateColorStep(s, currentSteps.length);
	const colorData = currentSteps[colorStep];

	subjectColorCache[s] = colorData;
	currentSteps.splice(colorStep, 1);

	return generateColorCss(baseColor, colorData);
}

const copyRawContent = computed(() => {
	return text.value.reduce<string>((acc, val) => {
		if (typeof val === "string") {
			return acc + val;
		}

		return acc + val[0];
	}, "");
});

const copyStructuredContent = computed(() => {
	try {
		return JSON.stringify(text.value);
	} catch (e) {
		return text.value.join("");
	}
});
</script>

<style scoped>
.CoreAnnotatedText {
	color: var(--primaryTextColor);
	line-height: 1.8;
}

.CoreAnnotatedText__markdown {
	display: flex;
	flex-direction: column;
	gap: 12px;
}
.CoreAnnotatedText__annotation,
.CoreAnnotatedText__markdown :deep(.CoreAnnotatedText__annotation) {
	flex-direction: row;
	align-items: center;
	background: rgba(255, 164, 33, 0.4);
	border-radius: 8px;
	padding: 2px 8px;
	overflow: hidden;
	line-height: 1;
	vertical-align: middle;
}

.CoreAnnotatedText__annotation__subject,
.CoreAnnotatedText__markdown :deep(.CoreAnnotatedText__annotation__subject) {
	display: inline-flex;
	font-size: 10px;
	margin-left: 14px;
	opacity: 0.5;
	position: relative;
	vertical-align: middle;

	&::after {
		content: "";
		border-left: 1px solid;
		opacity: 0.1;
		position: absolute;
		top: 0px;
		left: -9px;
		height: 10px;
	}
}
</style>
