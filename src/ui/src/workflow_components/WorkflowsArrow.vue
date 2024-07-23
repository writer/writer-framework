<template>
	<g @click="handleClick">
		<path :d="pathD" :style="{ stroke: props.arrow.color }"></path>
		<path
			:d="pathD"
			:style="{
				stroke: props.arrow.color,
				strokeWidth: 12,
				opacity: isSelected ? `0.2` : `0`,
			}"
		></path>
	</g>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
	arrow: {
		x1: number;
		y1: number;
		x2: number;
		y2: number;
		color: string;
	};
}>();

const isSelected = ref(false);

function handleClick() {
	isSelected.value = true;
}

const pathD = computed(() => {
	const xDif = props.arrow.x2 - props.arrow.x1;
	const yDif = props.arrow.y2 - props.arrow.y1;

	const protrusionLength = Math.max(
		Math.min(
			Math.sqrt(xDif * xDif + yDif * yDif),
			0.8 * Math.abs(xDif),
			50,
		),
		0,
	);

	const points = [
		{ x: props.arrow.x1, y: props.arrow.y1 },
		{ x: props.arrow.x1 + protrusionLength, y: props.arrow.y1 },
		{
			x: props.arrow.x1 + protrusionLength,
			y: props.arrow.y1 + yDif * 0.25,
		},
		{ x: props.arrow.x1 + xDif * 0.5, y: props.arrow.y1 + yDif * 0.5 },
		{
			x: props.arrow.x2 - protrusionLength,
			y: props.arrow.y1 + yDif * 0.75,
		},
		{ x: props.arrow.x2 - protrusionLength, y: props.arrow.y2 },
		{ x: props.arrow.x2, y: props.arrow.y2 },
	];

	let s: string;

	if (xDif > 50) {
		s = `M ${points[0].x} ${points[0].y}`;
		s += `C ${points[3].x} ${points[0].y}, ${points[3].x} ${points[6].y}, ${points[6].x} ${points[6].y}`;
	} else {
		s = `M ${points[0].x} ${points[0].y}`;
		s += `C ${points[1].x} ${points[1].y}, ${points[2].x} ${points[2].y}, ${points[3].x} ${points[3].y}`;
		s += `C ${points[4].x} ${points[4].y}, ${points[5].x} ${points[5].y}, ${points[6].x} ${points[6].y}`;
	}

	return s;
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.WorkflowsArrow {
}

path {
	fill: none;
}
</style>
