<template>
	<div
		ref="rootEl"
		class="CoreProgressBar"
		:class="{ 'CoreProgressBar--clickable': isClickable }"
		role="progressbar"
		:aria-valuetext="progression === undefined ? null : progressionText"
		:aria-valuemin="min"
		:aria-valuemax="max"
		:aria-valuenow="progression === undefined ? null : value"
		:aria-busy="progression < 1 || progression === undefined"
		:tabindex="isClickable ? '0' : null"
		@keydown.enter="handleClick"
		@click="handleClick"
	>
		<div v-if="label || displayPercentage" class="CoreProgressBar__title">
			<label v-if="label" class="CoreProgressBar__title__label">{{
				label
			}}</label>
			<span
				v-if="displayPercentage && progression !== undefined"
				class="CoreProgressBar__title__progress"
				>{{ progressionText }}</span
			>
		</div>
		<div class="CoreProgressBar__bar">
			<div
				class="CoreProgressBar__bar__value"
				:class="{
					'CoreProgressBar__bar__value--indeterminate':
						progression === undefined,
				}"
				:style="progressValueStyle"
			></div>
		</div>
	</div>
</template>

<script lang="ts">
import {
	FieldCategory,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";
import {
	cssClasses,
	accentColor,
	primaryTextColor,
	separatorColor,
	baseYesNoField,
} from "@/renderer/sharedStyleFields";

const clickHandlerStub = `
def handle_progress_bar_click():
	print("The progress bar was clicked")`;

const description = "A component to display a progression.";

const definition: WriterComponentDefinition = {
	name: "Progress Bar",
	description,
	category: "Content",
	allowedChildrenTypes: ["*"],
	fields: {
		label: {
			name: "Label",
			type: FieldType.Text,
			default: "",
		},
		value: {
			name: "Value",
			type: FieldType.Number,
		},
		min: {
			name: "Minimum value",
			type: FieldType.Number,
			default: "0",
		},
		max: {
			name: "Maximum value",
			type: FieldType.Number,
			default: "1",
		},
		displayPercentage: {
			...baseYesNoField,
			name: "Display percentage",
			default: "no",
			category: FieldCategory.Style,
		},
		accentColor,
		primaryTextColor,
		separatorColor,
		cssClasses,
	},
	events: {
		"wf-click": {
			desc: "Triggered when the progress bar is clicked.",
			stub: clickHandlerStub.trim(),
		},
	},
};

export default { writer: definition };
</script>

<script setup lang="ts">
import { CSSProperties, computed, inject, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";
import { getClick } from "@/renderer/syntheticEvents";
import { usePercentageFormatter } from "@/composables/useFormatter";

const rootEl = useTemplateRef("rootEl");
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const wf = inject(injectionKeys.core);

const label = computed(() => String(fields.label?.value));
const value = computed(() => Number(fields.value.value));
const min = computed(() => Number(fields.min.value));
const max = computed(() => Number(fields.max.value));
const displayPercentage = computed(() =>
	Boolean(fields.displayPercentage.value),
);

const progression = computed<number | undefined>(() => {
	if (value.value === undefined || Number.isNaN(value.value)) {
		return undefined;
	}
	return (value.value - min.value) / (max.value - min.value);
});

const progressionText = usePercentageFormatter(progression);

const progressValueStyle = computed<CSSProperties>(() => ({
	width:
		progression.value === undefined
			? undefined
			: `${progression.value * 100}%`,
}));

const isClickable = computed(() => {
	const component = wf.getComponentById(componentId);
	return typeof component.handlers?.["wf-click"] !== "undefined";
});

function handleClick(ev: MouseEvent | KeyboardEvent) {
	if (!isClickable.value) return;
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreProgressBar--clickable {
	cursor: pointer;
}

.CoreProgressBar__bar {
	height: 16px;
	width: 100%;
	border-radius: 4px;
	background-color: var(--separatorColor);
	position: relative;
	overflow-x: hidden;
}
.CoreProgressBar__bar__value {
	background-color: var(--accentColor);
	height: 100%;
	border-radius: 4px;
	transition: width 0.2s ease-in-out;
}
.CoreProgressBar__bar__text {
	position: absolute;
	left: 8px;
	line-height: 24px;
}

.CoreProgressBar__title {
	display: flex;
	gap: 8px;

	font-size: 0.875rem;
	color: var(--primaryTextColor);
	margin-bottom: 4px;
	line-height: 150%;
}

.CoreProgressBar__title__label {
	flex-grow: 1;
}
.CoreProgressBar__title__progress {
	text-align: right;
}

.CoreProgressBar__bar__value--indeterminate {
	position: absolute;
	animation: indeterminateAnimation 2s ease-in-out infinite;
	width: 25%;
}

@keyframes indeterminateAnimation {
	0% {
		left: -25%;
		right: 100%;
	}
	60% {
		left: 100%;
		right: -25%;
	}
	100% {
		left: 100%;
		right: -25%;
	}
}
</style>
