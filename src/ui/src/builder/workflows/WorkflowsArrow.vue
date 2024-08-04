<template>
	<g>
		<!-- Arrow Line -->
		<line
			:x1="props.arrow.x1"
			:y1="props.arrow.y1"
			:x2="props.arrow.x2"
			:y2="props.arrow.y2"
			:stroke="props.arrow.color"
			stroke-width="1"
			marker-end="url(#arrowhead)"
		/>
	</g>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
	arrow: {
		x1: number;
		y1: number;
		x2: number;
		y2: number;
		color: string;
	};
}>();
</script>

<style scoped>
@import "../sharedStyles.css";

.WorkflowsArrow {
}
</style>
