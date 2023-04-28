<template>
	<div class="CoreMetric" :style="rootStyle">
		<div class="name" v-if="fields.name">{{ fields.name }}</div>
		<div class="description" v-if="fields.description">
			{{ fields.description }}
		</div>
		<div class="value">{{ fields.metricValue }}</div>
		<div class="note" v-if="noteWithoutPrefix">{{ noteWithoutPrefix }}</div>
	</div>
</template>

<script lang="ts">
const description =
	"A component that prominently displays a metric value and associated information.";

export default {
	streamsync: {
		name: "Metric",
		description,
		category: "Content",
		fields: {
			name: {
				name: "Name",
				default: "Metric",
				type: FieldType.Text,
			},
			metricValue: {
				name: "Value",
				default: "0",
				type: FieldType.Text,
				desc: "The main value to be displayed. It's not limited to numbers.",
			},
			description: {
				name: "Description",
				type: FieldType.Text,
			},
			note: {
				name: "Note",
				init: "+Pass",
				type: FieldType.Text,
				desc: "Prefix with '+' for a positive message, with '-' for a negative message.",
			},
			primaryTextColor,
			secondaryTextColor,
			positiveColor: {
				name: "Positive",
				default: "#00B800",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			neutralColor: {
				name: "Neutral",
				default: "var(--secondaryTextColor)",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			negativeColor: {
				name: "Negative",
				default: "#FB0000",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
		},
		previewField: "name",
	},
};
</script>
<script setup lang="ts">
import { computed, inject } from "vue";
import { FieldCategory, FieldType } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import {
	primaryTextColor,
	secondaryTextColor,
} from "../renderer/sharedStyleFields";
const fields = inject(injectionKeys.evaluatedFields);

const sentiment = computed(() => {
	const note: string = fields.value?.note;
	if (!note) return "neutral";
	const firstChar = note.charAt(0);
	if (firstChar == "+") {
		return "positive";
	} else if (firstChar == "-") {
		return "negative";
	}
	return "neutral";
});

const noteWithoutPrefix = computed(() => {
	const note: string = fields.value?.note;
	if (!note) return;
	const firstChar = note.charAt(0);
	if (firstChar == "+" || firstChar == "-") {
		return note.substring(1);
	}
	return note;
});

const rootStyle = computed(() => {
	if (!fields.value) return;
	const sentimentColors = {
		positive: fields.value.positiveColor,
		neutral: fields.value.neutralColor,
		negative: fields.value.negativeColor,
	};
	return {
		"--messageActiveSentimentColor": sentimentColors[sentiment.value],
	};
});
</script>
<style scoped>
@import "../renderer/sharedStyles.css";

.CoreMetric {
	color: var(--primaryTextColor);
	border-left: 4px solid transparent;
	padding-left: 16px;
	display: flex;
	flex-direction: column;
	gap: 8px;
	border-color: var(--messageActiveSentimentColor);
}

.name {
	font-size: 0.9rem;
}

.description {
	font-size: 0.75rem;
	color: var(--secondaryTextColor);
}

.value {
	overflow: hidden;
	text-overflow: ellipsis;
	font-size: 1.6rem;
}

.note {
	font-size: 0.9rem;
	color: var(--messageActiveSentimentColor);
	filter: brightness(0.9);
}
</style>
