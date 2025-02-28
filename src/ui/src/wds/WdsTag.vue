<script lang="ts">
export type WdsTagVariant = "normal" | "category" | "status";
export type WdsTagSize = "normal" | "small";
</script>
<script setup lang="ts">
import { computed, PropType } from "vue";

const props = defineProps({
	text: { type: String, required: true },
	closable: { type: Boolean, required: false },
	size: { type: String as PropType<WdsTagSize>, default: "normal" },
	variant: { type: String as PropType<WdsTagVariant>, default: "normal" },
});

const classes = computed<string[]>(() => [
	`WdsTag--size-${props.size}`,
	`WdsTag--variant-${props.variant}`,
]);

defineEmits({
	close: () => true,
});
</script>

<template>
	<div class="WdsTag" :class="classes">
		<span class="WdsTag__text">{{ text }}</span>
		<button
			v-if="closable"
			role="button"
			class="WdsTag__close"
			@click.stop="$emit('close')"
		>
			<i class="material-symbols-outlined">close</i>
		</button>
	</div>
</template>

<style scoped>
.WdsTag {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 4px;
	border-radius: 12px;
	padding: 3px 12px;
}

.WdsTag--size-normal {
	font-size: 12px;
}
.WdsTag--size-small {
	font-size: 10px;
}

.WdsTag--variant-normal {
	background-color: var(--wdsColorBlue2);
}
.WdsTag--variant-normal:hover {
	background-color: var(--wdsColorBlue3);
}

.WdsTag__close {
	border: none;
	background-color: transparent;

	display: flex;
	align-items: center;
	justify-content: center;

	cursor: pointer;
}
</style>
