<template>
	<div class="CorePlotlyGraph" ref="rootEl">
		<div ref="chartTargetEl" class="target"></div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../streamsyncTypes";

const description = "A component that displays Plotly graphs.";

const docs = ``;

const defaultSpec = {
	data: [
		{
			x: ["a", "b", "c"],
			y: [22, 25, 29],
			type: "bar",
		},
	],
};

export default {
	streamsync: {
		name: "Plotly Graph",
		description,
		docs,
		category: "Content",
		fields: {
			spec: {
				name: "Graph specification",
				default: JSON.stringify(defaultSpec, null, 2),
				desc: "Plotly graph specification. Pass a Plotly graph using state or paste a JSON specification.",
				type: FieldType.Object,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, onMounted, Ref, ref, watch, nextTick } from "vue";
import injectionKeys from "../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const chartTargetEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);

const renderChart = async () => {
	if (import.meta.env.SSR) return;

	if (!fields.spec.value || !chartTargetEl.value) return;
	const Plotly = await import("plotly.js-dist-min");

	if (rootEl.value.clientHeight == 0) return;

	Plotly.newPlot(chartTargetEl.value, fields.spec.value);
};

watch(
	() => fields.spec.value,
	(spec) => {
		if (!spec) return;
		renderChart();
	}
);

onMounted(() => {
	renderChart();
	new ResizeObserver(renderChart).observe(rootEl.value, {
		box: "border-box",
	});
});
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CorePlotlyGraph {
	min-height: 1px;
}

.target {
	overflow: hidden;
}
</style>
