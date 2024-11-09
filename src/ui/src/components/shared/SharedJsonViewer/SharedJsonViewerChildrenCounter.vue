<template>
	<span>{{ text }}</span>
</template>

<script setup lang="ts">
import { PropType, computed } from "vue";
import {
	getJSONLength,
	isJSONArray,
	isJSONObject,
} from "./SharedJsonViewer.utils";
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
});

const printObject = (length: number) => `Object{${length}}`;
const printArray = (length: number) => `Array[${length}]`;

const text = computed(() => {
	const count = getJSONLength(props.data);

	if (count === 0) return printObject(0);
	if (isJSONArray(props.data)) return printArray(count);
	if (isJSONObject(props.data)) return printObject(count);
	return printObject(0);
});
</script>

<style scoped>
span {
	color: var(--secondaryTextColor);
	font-family: monospace;
	font-size: 12px;
}
</style>
