<template>
	<div
		v-if="shouldDisplay"
		ref="rootEl"
		class="CoreText"
		:style="rootStyle"
		@click="handleClick"
	>
		<BaseEmptiness v-if="isEmpty" :component-id="componentId" />
		<template v-else>
			<BaseMarkdown
				v-if="fields.useMarkdown.value"
				:raw-text="fields.text.value"
				:style="contentStyle"
			>
			</BaseMarkdown>
			<p v-else class="plainText" :style="contentStyle">
				{{ fields.text.value }}
			</p>
		</template>
	</div>
</template>

<script lang="ts">
import {
	baseYesNoField,
	cssClasses,
	primaryTextColor,
} from "@/renderer/sharedStyleFields";
import { getClick } from "@/renderer/syntheticEvents";
import { FieldCategory, FieldControl, FieldType } from "@/writerTypes";

const clickHandlerStub = `
def click_handler(state):

	# Increment counter when the text is clicked

	state["counter"] += 1`;

const description =
	"A component to display plain text or formatted text using Markdown syntax.";

export default {
	writer: {
		name: "Text",
		description,
		category: "Content",
		fields: {
			text: {
				name: "Text",
				init: "Text",
				desc: "Add text directly, or reference state elements with @{my_text}.",
				type: FieldType.Text,
				control: FieldControl.Textarea,
			},
			useMarkdown: {
				...baseYesNoField,
				name: "Use Markdown",
				desc: "The Markdown output will be sanitised; unsafe elements will be removed.",
				default: "no",
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
			cssClasses,
		},
		events: {
			"wf-click": {
				desc: "Capture single clicks.",
				stub: clickHandlerStub.trim(),
			},
		},
		previewField: "text",
	},
};
</script>

<script setup lang="ts">
import { computed, inject, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import BaseEmptiness from "../base/BaseEmptiness.vue";
import BaseMarkdown from "../base/BaseMarkdown.vue";

const rootEl = useTemplateRef("rootEl");
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const wf = inject(injectionKeys.core);

const isBeingEdited = inject(injectionKeys.isBeingEdited);
const isEmpty = computed(() => !fields.text.value);
const shouldDisplay = computed(() => !isEmpty.value || isBeingEdited.value);

const rootStyle = computed(() => {
	const component = wf.getComponentById(componentId);
	const isClickHandled =
		typeof component.handlers?.["wf-click"] !== "undefined";

	return {
		cursor: isClickHandled ? "pointer" : "unset",
	};
});

const contentStyle = computed(() => {
	return {
		"text-align": fields.alignment.value,
	};
});

function handleClick(ev: MouseEvent) {
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreText {
	color: var(--primaryTextColor);
	line-height: 140%;
	white-space: pre-wrap;
	max-width: 100%;
	overflow: hidden;
	font-size: 0.875rem;
	font-weight: 400;
}

.CoreText:deep(p) {
	overflow: hidden;
	text-overflow: ellipsis;
}

.CoreText ol,
.CoreText ul {
	white-space: normal;
}

.CoreText img {
	width: 100%;
}
</style>
