<template>
	<div class="WorkflowsLifeLoading">
		<div
			v-for="(cell, cellId) in cells"
			:key="cellId"
			class="cell"
			:style="{
				left: `${cell.x}px`,
				top: `${cell.y}px`,
				height: `${cell.size}px`,
				width: `${cell.size}px`,
				opacity: `${cell.opacity}`,
			}"
		></div>
	</div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

const tickN = ref(0);

const cellsInitValue = [
	{
		x: 200,
		y: 200,
		size: 2,
		opacity: 1,
	},
];

const cells = ref(cellsInitValue);

function lifeTick() {
	tickN.value++;

	cells.value = cells.value
		.map((c) => ({
			x: c.x - 0.6,
			y: c.y - 0.6,
			opacity: c.opacity - 0.006,
			size: Math.min(c.size + 0.8, 60),
		}))
		.filter((c) => {
			return c.opacity > 0;
		});

	if (cells.value.length == 0) {
		resetCells();
	} else if (tickN.value % 50 == 0 && cells.value.length < 100) {
		cells.value = cells.value

			.map((c) => {
				const ca = {
					...c,
					opacity: 1.0,
					size: 2,
					x: Math.min(c.x + Math.random() * 160 - 80, 240),
					y: Math.min(c.y + Math.random() * 160 - 80, 240),
				};
				const cb = {
					...c,
					opacity: 1.0,
					size: 2,
					x: Math.min(c.x + Math.random() * 160 - 80, 240),
					y: Math.min(c.y + Math.random() * 160 - 80, 240),
				};
				return [c, ca, cb];
			})
			.flat();
	}

	setTimeout(lifeTick, 20);
}

function resetCells() {
	cells.value = [...cellsInitValue];
	tickN.value = 0;
}

onMounted(() => {
	resetCells();
	lifeTick();
});
</script>

<style scoped>
.WorkflowsLifeLoading {
	position: relative;
	width: 240px;
	height: 240px;
	background: linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%);
	border-radius: 50%;
	overflow: hidden;
}

.cell {
	position: absolute;
	background: #ee46d3;
	border-radius: 50%;
}
</style>
