<script setup lang="ts">
import { bigIntReplacer } from "@/core/serializer";
import { computed } from "vue";

const props = defineProps({
	value: { validator: () => true, required: true },
});

const text = computed(() => JSON.stringify(props.value, bigIntReplacer));
</script>

<template>
	<div class="CoreDataframeCellUnknown">
		{{ text }}
	</div>
</template>

<style scoped>
.CoreDataframeCellUnknown {
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
	display: inline-block;
}
</style>
