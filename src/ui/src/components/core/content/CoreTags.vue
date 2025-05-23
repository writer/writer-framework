<template>
	<div
		v-if="
			isBeingEdited || Object.entries(fields.tags.value ?? []).length > 0
		"
		ref="rootEl"
		class="CoreTags"
	>
		<template v-if="Object.entries(fields.tags.value ?? []).length > 0">
			<p
				v-for="(tagDesc, tagId) in fields.tags.value"
				:key="tagId"
				class="CoreTags__tag"
				:style="{ background: generateColor(tagId) }"
				@click="handleTagClick(tagId)"
			>
				<span
					:data-writer-tooltip="tagDesc"
					data-writer-tooltip-strategy="overflow"
					>{{ tagDesc }}</span
				>
			</p>
		</template>
		<p v-else class="CoreTags__tag CoreTags__tag--empty">
			<span>Empty Tags</span>
		</p>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";
import {
	baseYesNoField,
	cssClasses,
	primaryTextColor,
} from "@/renderer/sharedStyleFields";
import { WdsColor } from "@/wds/tokens";
import { useComponentLinkedBlueprints } from "@/composables/useComponentBlueprints";

const clickHandlerStub = `
def handle_tag_click(state, payload):
	state["selected_tag_id"] = payload`;

const description = "A component to display coloured tag pills.";

export default {
	writer: {
		name: "Tags",
		description,
		category: "Content",
		fields: {
			tags: {
				name: "Tags",
				desc: "Key-value object with tags. Must be a JSON string or a state reference to a dictionary.",
				type: FieldType.KeyValue,
				default: "{}",
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
				...baseYesNoField,
				name: "Rotate hue",
				desc: "If active, rotates the hue depending on the content of the string. If turned off, the reference colour is always used.",
				default: "yes",
				category: FieldCategory.Style,
			},
			primaryTextColor,
			cssClasses,
		},
		events: {
			"wf-tag-click": {
				desc: "Triggered when a tag is clicked.",
				stub: clickHandlerStub.trim(),
				eventPayloadExample: "tagKey",
			},
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { computed, inject, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import chroma from "chroma-js";

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
const rootEl = useTemplateRef("rootEl");
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const wf = inject(injectionKeys.core);
const isBeingEdited = inject(injectionKeys.isBeingEdited);

const { isLinked: hasLinkedBlueprint } = useComponentLinkedBlueprints(
	wf,
	componentId,
	"wf-tag-click",
);

const isClickable = computed(() => {
	if (hasLinkedBlueprint.value) return true;
	const component = wf.getComponentById(componentId);
	return typeof component.handlers?.["wf-tag-click"] !== "undefined";
});

function generateColor(s: string | number) {
	if (!fields.rotateHue.value) {
		return fields.referenceColor.value;
	}
	const baseColor = chroma(fields.referenceColor.value);
	const colorStep = COLOR_STEPS[calculateColorStep(s)];
	let genColor = baseColor
		.set(
			"hsl.h",
			`${Math.sign(colorStep.h) == -1 ? "-" : "+"}${Math.abs(colorStep.h)}`,
		)
		.set(
			"hsl.s",
			`${Math.sign(colorStep.s) == -1 ? "-" : "+"}${Math.abs(colorStep.s / 100.0)}`,
		)
		.set(
			"hsl.l",
			`${Math.sign(colorStep.l) == -1 ? "-" : "+"}${Math.abs(colorStep.l / 100.0)}`,
		);
	return genColor.css();
}

function calculateColorStep(s: string | number) {
	let hash = (fields.seed.value * 52673) & 0xffffffff;
	for (let i = 0; i < s.length; i++) {
		hash = ((i + 1) * s.charCodeAt(i)) ^ (hash & 0xffffffff);
	}
	const step = Math.abs(hash) % COLOR_STEPS.length;
	return step;
}

function handleTagClick(tagId: string | number) {
	const event = new CustomEvent("wf-tag-click", {
		detail: {
			payload: tagId,
		},
	});
	rootEl.value.dispatchEvent(event);
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreTags {
	display: flex;
	gap: 8px;
	flex-wrap: wrap;
	align-items: center;
}

.CoreTags__tag {
	height: fit-content;
	padding: 6px 12px 6px 12px;
	border-radius: 16px;
	font-size: 0.75rem;
	line-height: 100%;
	font-weight: 500;
	letter-spacing: 1.3px;
	text-transform: uppercase;
	color: var(--primaryTextColor);
	display: flex;
	align-items: center;
	gap: 4px;
	cursor: v-bind("isClickable ? 'pointer' : 'auto'");
	overflow: hidden;
}
.CoreTags__tag span {
	overflow: hidden;
	text-overflow: ellipsis;
}

.CoreTags__tag--empty {
	background-color: var(--separatorColor);
	color: var(--primaryTextColor);
}

.CoreTags__tag--empty span {
	opacity: 0.8;
}
</style>
