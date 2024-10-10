<template>
	<g
		class="WorkflowArrow"
		tabindex="0"
		data-writer-unselectable="true"
		:class="{ engaged: isEngaged }"
	>
		<path :d="pathD" :style="{ stroke: arrow.color }"></path>
		<path
			:d="pathD"
			:style="{
				stroke: arrow.color,
				strokeWidth: 12,
				opacity: isSelected ? `0.2` : `0`,
			}"
		></path>
		<g
			v-if="isSelected"
			class="delete"
			tabindex="0"
			aria-label="Delete relation"
			@click="handleDeleteClick"
			@keypress.enter="handleDeleteClick"
		>
			<circle :cx="points[3].x" :cy="points[3].y" r="12" />
			<line
				class="cross"
				:x1="points[3].x - 4"
				:y1="points[3].y - 4"
				:x2="points[3].x + 4"
				:y2="points[3].y + 4"
				:stroke="arrow.color"
				stroke-width="2"
			/>
			<line
				class="cross"
				:x1="points[3].x + 4"
				:y1="points[3].y - 4"
				:x2="points[3].x - 4"
				:y2="points[3].y + 4"
				:stroke="arrow.color"
				stroke-width="2"
			/>
		</g>
	</g>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { type WorkflowArrowData } from "../WorkflowsWorkflow.vue";

const PROTRUSION_LENGTH = 30;
const emit = defineEmits(["delete"]);

const props = defineProps<{
	arrow: WorkflowArrowData;
	isSelected: boolean;
	isEngaged: boolean;
}>();

const points = computed(() => {
	const xDif = props.arrow.x2 - props.arrow.x1;
	const yDif = props.arrow.y2 - props.arrow.y1;

	const ps = [
		{ x: props.arrow.x1, y: props.arrow.y1 },
		{ x: props.arrow.x1 + PROTRUSION_LENGTH, y: props.arrow.y1 },
		{
			x: props.arrow.x1 + PROTRUSION_LENGTH,
			y: props.arrow.y1 + yDif * 0.25,
		},
		{ x: props.arrow.x1 + xDif * 0.5, y: props.arrow.y1 + yDif * 0.5 },
		{
			x: props.arrow.x2 - PROTRUSION_LENGTH,
			y: props.arrow.y1 + yDif * 0.75,
		},
		{ x: props.arrow.x2 - PROTRUSION_LENGTH, y: props.arrow.y2 },
		{ x: props.arrow.x2, y: props.arrow.y2 },
	];
	return ps;
});

const pathD = computed(() => {
	const xDif = props.arrow.x2 - props.arrow.x1;
	const ps = points.value;
	let s: string;

	if (xDif > PROTRUSION_LENGTH) {
		s = `M ${ps[0].x} ${ps[0].y}`;
		s += `C ${ps[3].x} ${ps[0].y}, ${ps[3].x} ${ps[6].y}, ${ps[6].x} ${ps[6].y}`;
	} else {
		s = `M ${ps[0].x} ${ps[0].y}`;
		s += `C ${ps[1].x} ${ps[1].y}, ${ps[2].x} ${ps[2].y}, ${ps[3].x} ${ps[3].y}`;
		s += `C ${ps[4].x} ${ps[4].y}, ${ps[5].x} ${ps[5].y}, ${ps[6].x} ${ps[6].y}`;
	}

	return s;
});

function handleDeleteClick() {
	emit("delete");
}
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.WorkflowArrow:not(.engaged):not(:hover) {
	filter: grayscale();
}

g {
	outline: none;
}

path {
	fill: none;
}

circle {
	fill: white;
	filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.2));
}

g.delete .cross {
	stroke: black;
}
</style>
