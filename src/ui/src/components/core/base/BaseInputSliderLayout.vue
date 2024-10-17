<template>
	<div
		role="slider"
		:aria-valuemin="min"
		:aria-valuemax="max"
		class="BaseInputRange"
		:class="{
			'BaseInputRange--popover-always-visible':
				popoverDisplayMode === 'always',
		}"
	>
		<slot />
	</div>
</template>

<script setup lang="ts">
import { PropType } from "vue";

defineProps({
	min: { type: Number, default: 0 },
	max: { type: Number, default: 100 },
	popoverDisplayMode: {
		type: String as PropType<"always" | "onChange">,
		default: "onChange",
	},
});
</script>

<style scoped>
.BaseInputRange {
	--thumb-color: var(--accentColor);
	--thumb-shadow-color: rgba(228, 231, 237, 0.4);
	--slider-color: var(--softenedAccentColor);
	--slider-bg-color: var(--separatorColor);
	--popover-bg-color: var(--popoverBackgroundColor, rgba(0, 0, 0, 1));
	width: 100%;

	position: relative;
	padding-top: 5px;
	padding-bottom: 5px;
}
.BaseInputRange--popover-always-visible {
	/* add extra margin to make sure the popover does not overflow on something */
	margin-top: 24px;
}

:deep(.BaseInputRange__slider) {
	height: 8px;
	width: 100%;
	border-radius: 4px;
	background-color: var(--slider-bg-color);
}

:deep(.BaseInputRange__slider__progress) {
	height: 100%;
	max-width: 100%;
	border-radius: 4px;
	background-color: var(--slider-color);
}
</style>
