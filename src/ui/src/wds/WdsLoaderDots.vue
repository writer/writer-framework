<script setup lang="ts">
import { WdsColor } from "./tokens";

defineProps({
	color: { type: String, required: false, default: WdsColor.Blue5 },
	size: { type: Number, required: false, default: 16 },
});
</script>

<template>
	<div
		class="WdsLoaderDots"
		:style="{ color: color, '--dot-size': `${size / 4}px` }"
	>
		<span class="WdsLoaderDots__dot"></span>
		<span class="WdsLoaderDots__dot WdsLoaderDots__dot--delay-1"></span>
		<span class="WdsLoaderDots__dot WdsLoaderDots__dot--delay-2"></span>
	</div>
</template>

<style scoped>
.WdsLoaderDots {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: var(--dot-size, 4px);
	width: fit-content;
	height: fit-content;
}

.WdsLoaderDots__dot {
	display: inline-flex;
	width: var(--dot-size, 4px);
	height: var(--dot-size, 4px);
	border-radius: 50%;
	background-color: currentColor;
	will-change: transform;
	animation: loader 1.4s infinite ease;
}

.WdsLoaderDots__dot--delay-1 {
	animation-delay: 350ms;
}

.WdsLoaderDots__dot--delay-2 {
	animation-delay: 700ms;
}

@keyframes loader {
	0% {
		transform: scale(1, 1);
	}
	50% {
		transform: scale(2, 2);
	}
	100% {
		transform: scale(1, 1);
	}
}
</style>
