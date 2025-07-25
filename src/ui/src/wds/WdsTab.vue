<template>
	<button
		class="WdsTab"
		:class="{
			'WdsTab--disabled': disabled,
			'WdsTab--selected': selected,
			'WdsTab--variant-bar': variant === 'bar',
			'WdsTab--variant-chip': variant === 'chip',
		}"
		type="button"
		:disabled="Boolean(disabled)"
		:data-writer-tooltip="tooltip"
		@click="$emit('click')"
	>
		<slot />
		<div v-if="variant === 'bar'" class="WdsTab__indicator"></div>
	</button>
</template>

<script lang="ts">
export type WdsTabVariant = "chip" | "bar";
</script>

<script setup lang="ts">
import { computed, PropType } from "vue";

const props = defineProps({
	disabled: { type: [Boolean, String], default: undefined },
	selected: { type: Boolean },
	variant: {
		type: String as PropType<WdsTabVariant>,
		required: true,
	},
});

const tooltip = computed(() =>
	typeof props.disabled === "string" ? props.disabled : undefined,
);

defineEmits({
	click: () => true,
});
</script>

<style scoped>
.WdsTab {
	/* reset button */
	position: relative;
	border: none;
	background-color: transparent;
	cursor: pointer;
}

.WdsTab__indicator {
	pointer-events: none;
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	height: 2px;
	width: 100%;
	background: currentColor;
	opacity: 0;
}

.WdsTab--disabled {
	cursor: not-allowed;
}

.WdsTab--variant-bar {
	padding: 10px 0;
	font-size: 14px;
	line-height: 180%;
	color: var(--wdsColorGray5);
}

.WdsTab--variant-bar.WdsTab--selected {
	color: var(--wdsColorBlack);
}

.WdsTab--variant-bar.WdsTab--selected .WdsTab__indicator {
	opacity: 1;
}

.WdsTab--variant-chip {
	padding: 4px 20px 4px 20px;
	border-radius: 8px;
}

.WdsTab--variant-chip:hover {
	background-color: var(--wdsColorBlue1);
}

.WdsTab--variant-chip.WdsTab--selected {
	background-color: var(--wdsColorBlue2);
}

.WdsTab--variant-chip.WdsTab--disabled {
	color: var(--wdsColorGray4);
}
</style>
