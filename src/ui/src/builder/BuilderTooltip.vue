<template>
	<div
		v-show="isActive"
		ref="rootEl"
		class="BuilderTooltip"
		:style="rootStyle"
	>
		<div class="arrow" :class="tooltipPlacement"></div>
		<div class="text">
			{{ tooltipText }}
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	ComputedRef,
	nextTick,
	onMounted,
	onUnmounted,
	ref,
} from "vue";

const DELAY_MS = 200;
const DEFAULT_GAP_PX = 4;

const rootEl = ref(null);
const isActive = ref(false);
const tooltipText = ref<ComputedRef | string | null>(null);
let trackedElement: HTMLElement | null = null;
let trackedElementObserver: MutationObserver | null = null;
const tooltipPlacement = ref<string>("top");
const position = ref<{
	top: number;
	left: number;
}>({ top: 0, left: 0 });

async function setUpAndShowTooltip() {
	tooltipText.value = trackedElement.dataset.writerTooltip;
	const gapPx = trackedElement.dataset.writerTooltipGap
		? parseInt(trackedElement.dataset.writerTooltipGap)
		: DEFAULT_GAP_PX;
	isActive.value = true;
	await nextTick();
	const { x, y, width, height } = trackedElement.getBoundingClientRect();
	const { width: tooltipWidth, height: tooltipHeight } =
		rootEl.value.getBoundingClientRect();

	switch (tooltipPlacement.value) {
		case "top":
			position.value.top = y - tooltipHeight - gapPx;
			position.value.left = x + width / 2 - tooltipWidth / 2;
			break;
		case "right":
			position.value.top = y + height / 2 - tooltipHeight / 2;
			position.value.left = x + width + gapPx;
			break;
		case "left":
			position.value.left = x - tooltipWidth - gapPx;
			position.value.top = y + height / 2 - tooltipHeight / 2;
			break;
		case "bottom":
			position.value.top = y + height + gapPx;
			position.value.left = x + width / 2 - tooltipWidth / 2;
			break;
	}
}

function handleMouseover(ev: MouseEvent) {
	const el = ev.target as HTMLElement;

	const tooltippedEl = el.closest("[data-writer-tooltip]") as HTMLElement;
	if (!tooltippedEl) {
		isActive.value = false;
		trackedElement = null;
		return;
	} else if (trackedElement !== tooltippedEl) {
		isActive.value = false;
	}
	trackedElement = tooltippedEl;

	tooltipPlacement.value =
		trackedElement.dataset.writerTooltipPlacement ?? "top";
	setTimeout(() => confirmTooltip(tooltippedEl), DELAY_MS);
}

async function confirmTooltip(el: HTMLElement) {
	if (el !== trackedElement) {
		return;
	}
	trackedElementObserver?.disconnect();
	trackedElementObserver = new MutationObserver(setUpAndShowTooltip);
	trackedElementObserver.observe(trackedElement, {
		attributes: true,
		attributeFilter: [
			"data-writer-tooltip",
			"data-writer-tooltip-placement",
		],
	});
	setUpAndShowTooltip();
}

const rootStyle = computed(() => {
	const { top, left } = position.value;
	return {
		top: `${top}px`,
		left: `${left}px`,
	};
});

onMounted(() => {
	const el = document.documentElement;
	el.addEventListener("mouseover", handleMouseover);
});

onUnmounted(() => {
	const el = document.documentElement;
	el.removeEventListener("mouseover", handleMouseover);
	trackedElementObserver?.disconnect();
});
</script>

<style scoped>
.BuilderTooltip {
	color: white;
	position: absolute;
	font-size: 12px;
	display: content;
	max-width: 260px;
	filter: drop-shadow(0px 0px 12px rgba(0, 0, 0, 0.16));
}

.arrow {
	position: absolute;
	margin: auto;
	background-color: black;
	width: 14px;
	height: 14px;
	transform: rotate(45deg);
}

.arrow.bottom {
	top: 0;
	right: 0;
	left: 0;
}

.arrow.top {
	bottom: 0;
	right: 0;
	left: 0;
}

.arrow.right {
	bottom: 0;
	top: 0;
	left: 0;
}

.arrow.left {
	bottom: 0;
	top: 0;
	right: 0;
}

.text {
	padding: 10px 12px 10px 12px;
	border-radius: 8px;
	background-color: black;
	margin: 4px;
	position: relative;
	z-index: 1;
}
</style>
