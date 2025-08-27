<template>
	<span class="SharedJsonViewerValue">{{ dataFormatted }}</span>
</template>

<script setup lang="ts">
import { PropType, computed } from "vue";
import type { JsonData } from "./SharedJsonViewer.vue";

const props = defineProps({
	data: {
		type: [
			String,
			Number,
			Boolean,
			Object,
			Array,
			null,
		] as PropType<JsonData>,
		required: true,
	},
	maxValueLength: {
		type: Number,
		default: 1_000,
	},
});

const dataFormatted = computed(() => {
	const data = JSON.stringify(props.data);
	if (data.length <= props.maxValueLength) return data;
	return `${data.slice(0, props.maxValueLength)}..."`;
});
</script>

<style scoped>
.SharedJsonViewerValue {
	font-family: monospace;
	color: var(--secondaryTextColor);
	word-break: break-all;
}
</style>
