<script setup lang="ts">
import { bigIntReplacer } from "@/core/serializer";
import { computed } from "vue";

const props = defineProps({
	value: { validator: () => true, required: true },
	wrapText: { type: Boolean, required: false },
});

const text = computed(() => JSON.stringify(props.value, bigIntReplacer));
</script>

<template>
	<div class="CoreDataframeCellUnknown">
		<p :class="{ 'CoreDataframeCellUnknown__content--noWrap': !wrapText }">
			{{ text }}
		</p>
	</div>
</template>

<style scoped>
.CoreDataframeCellUnknown {
	width: 100%;
	font-size: inherit;

	border: 1px solid transparent;
	padding: 8.5px 12px 8.5px 12px;
	pointer-events: none;
}

.CoreDataframeCellUnknown__content--noWrap {
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
}
</style>
