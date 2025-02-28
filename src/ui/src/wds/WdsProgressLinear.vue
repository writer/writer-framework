<template>
	<svg
		:width="sizePx"
		:height="sizePx"
		:viewBox="viewBow"
		style="transform: rotate(-90deg)"
		role="progressbar"
		:aria-valuenow="progress"
		aria-valuemin="0"
		aria-valuemax="100"
	>
		<circle
			:r="radius"
			:cx="c"
			:cy="c"
			fill="transparent"
			:stroke="WdsColor.Blue1"
			:stroke-width="strokeWidth"
		></circle>
		<circle
			:r="radius"
			:cx="c"
			:cy="c"
			fill="transparent"
			:stroke="WdsColor.Blue5"
			:stroke-width="strokeWidth"
			:stroke-dasharray="strokeDasharray"
			:stroke-dashoffset="strokeDashoffset"
		></circle>
	</svg>
</template>

<script setup lang="ts">
import { WdsColor } from "@/wds/tokens";
import { computed } from "vue";

const props = defineProps({
	progress: { type: Number, required: false, default: 100 },
	sizePx: { type: Number, required: false, default: 12 },
	strokeWidth: { type: Number, required: false, default: 2 },
});

const c = computed(() => props.sizePx / 2);
const radius = computed(() => props.sizePx / 2 - props.strokeWidth / 2);

const strokeDasharray = computed(() => 2 * Math.PI * radius.value);
const strokeDashoffset = computed(
	() => strokeDasharray.value * ((100 - props.progress) / 100),
);

const viewBow = computed(() => `0 0 ${props.sizePx} ${props.sizePx}`);
</script>
