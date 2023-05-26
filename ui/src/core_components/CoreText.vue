<template>
	<div class="CoreText" :style="rootStyle">
		<template v-if="fields.useMarkdown.value == 'no'">
			<div class="plainText" :style="contentStyle">{{ fields.text.value }}</div>
		</template>
		<template v-else-if="fields.useMarkdown.value == 'yes'">
			<div
				class="markdown"
				:style="contentStyle"
				v-dompurify-html="unsanitisedMarkdownHtml"
			></div>
		</template>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../streamsyncTypes";
import { primaryTextColor } from "../renderer/sharedStyleFields";

const clickHandlerStub = `
def click_handler(state):

	# Increment counter when the text is clicked

	state["counter"] += 1`;

const description =
	"A component to display plain text or formatted text using Markdown syntax.";

export default {
	streamsync: {
		name: "Text",
		description,
		category: "Content",
		fields: {
			text: {
				name: "Text",
				default: "(No text)",
				init: "Text",
				type: FieldType.Text,
				control: "textarea",
			},
			useMarkdown: {
				name: "Use Markdown",
				desc: "The Markdown output will be sanitised; unsafe elements will be removed.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			alignment: {
				name: "Alignment",
				default: "left",
				type: FieldType.Text,
				options: {
					left: "Left",
					center: "Center",
					right: "Right",
				},
				category: FieldCategory.Style,
			},
			primaryTextColor,
		},
		events: {
			click: {
				desc: "Capture single clicks.",
				stub: clickHandlerStub.trim(),
			},
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { marked } from "marked";
import { computed, inject } from "vue";
import injectionKeys from "../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const ss = inject(injectionKeys.core);

const rootStyle = computed(() => {
	const component = ss.getComponentById(componentId);
	const isClickHandled = typeof component.handlers?.["click"] !== "undefined";

	return {
		cursor: isClickHandled ? "pointer" : "unset",
	};
});

const contentStyle = computed(() => {
	return {
		"text-align": fields.alignment.value,
	};
});

const unsanitisedMarkdownHtml = computed(() => {
	const unsanitisedHtml = marked.parse(fields.text.value).trim();
	return unsanitisedHtml;
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreText {
	color: var(--primaryTextColor);
	line-height: 1.5;
	white-space: pre-wrap;
	max-width: 100%;
	overflow: hidden;
}

.CoreText ol,
.CoreText ul {
	white-space: normal;
}

.CoreText img {
	width: 100%;
}

/*
Markdown styling
*/

.markdown:deep() h1,
.markdown:deep() h2,
.markdown:deep() h3,
.markdown:deep() h4 {
	font-weight: 300;
	margin: 0;
	color: var(--primaryTextColor);
}

.markdown:deep() h1 {
	font-size: 1.3rem;
}

.markdown:deep() h2 {
	font-size: 1rem;
}

.markdown:deep() h3 {
	font-size: 0.9rem;
}

.markdown:deep() h4 {
	text-transform: uppercase;
	font-weight: bold;
	font-size: 0.65rem;
	letter-spacing: 0.2ch;
}

.markdown:deep() ul,
.markdown:deep() ol {
	padding: 0;
	padding-inline-start: 0;
	margin-block-start: 0;
}

.markdown:deep() li {
	margin: 0 0 0 32px;
}

.markdown:deep() hr {
	border: none;
	border-top: 1px solid var(--separatorColor);
}

.markdown:deep() pre {
	background-color: var(--separatorColor);
	font-family: monospace;
	padding: 8px;
}

.markdown:deep() code {
	background-color: var(--separatorColor);
	font-family: monospace;
	padding: 2px;
}

.markdown:deep() pre > code {
	background-color: unset;
}
</style>
