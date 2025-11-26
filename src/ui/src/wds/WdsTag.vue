<script lang="ts">
export type WdsTagVariant =
	| "normal"
	| "category"
	| "status"
	| "success"
	| "error"
	| "warning"
	| "neutral";
export type WdsTagSize = "normal" | "small";
</script>
<script setup lang="ts">
import { computed, PropType } from "vue";
import WdsIcon from "./WdsIcon.vue";

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
			type="button"
			class="WdsTag__close"
			@click.stop="$emit('close')"
		>
			<WdsIcon name="x" />
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

.WdsTag--variant-success {
	background-color: var(--wdsColorGreen1);
	color: var(--wdsColorGreen6);
}

.WdsTag--variant-error {
	background-color: var(--wdsColorOrange1);
	color: var(--wdsColorOrange5);
}

.WdsTag--variant-warning {
	background-color: var(--wdsColorYellow1);
	color: var(--wdsColorYellow6);
}

.WdsTag--variant-neutral {
	background-color: var(--wdsColorGray2);
	color: var(--wdsColorGray6);
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
