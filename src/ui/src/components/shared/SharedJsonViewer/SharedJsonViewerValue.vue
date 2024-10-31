<template>
	<span class="SharedJsonViewerValue">{{ dataFormatted }}</span>
</template>

<script setup lang="ts">
import { PropType, computed } from "vue";
import type { JsonValue } from "./SharedJsonViewer.vue";

const props = defineProps({
	data: {
		type: [Object, String, Number] as PropType<JsonValue>,
		required: true,
	},
});

const dataFormatted = computed(() => JSON.stringify(props.data));
</script>

<style scoped>
.SharedJsonViewerValue {
	font-family: monospace;
	color: var(--secondaryTextColor);
}
</style>
