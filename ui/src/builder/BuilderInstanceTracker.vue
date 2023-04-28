<template>
	<div class="BuilderInstanceTracker" :style="rootStyle" ref="rootEl">
		<slot></slot>
	</div>
</template>
<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, Ref, ref, toRefs } from "vue";

const REFRESH_INTERVAL_MS = 200;

interface Props {
	instancePath: string;
	matchSize?: boolean;
	verticalOffsetPixels?: number;
	isOffBoundsAllowed?: boolean;
}
const props = defineProps<Props>();
const { instancePath, matchSize, verticalOffsetPixels, isOffBoundsAllowed } =
	toRefs(props);

type RootStyle = {
	top: string;
	left: string;
	width: string;
	height: string;
};

const rootStyle: Ref<RootStyle> = ref(null);
const timerId = ref(0);
const rootEl: Ref<HTMLElement> = ref(null);
const MIN_TOP_PX = 36;

const trackElement = (el: HTMLElement) => {
	const rendererEl = document.querySelector(".ComponentRenderer");
	const { top: elY, left: elX } = el.getBoundingClientRect();
	const { clientHeight: bodyHeight } = document.body;
	const { clientWidth: rendererWidth } = rendererEl;
	const { left: rendererX } = rendererEl.getBoundingClientRect();
	let { clientHeight: contentsHeight, clientWidth: contentsWidth } =
		matchSize?.value ? el : rootEl.value;
	let yAdjustment = verticalOffsetPixels?.value
		? verticalOffsetPixels.value
		: 0;

	let trackerX = elX;
	let trackerY = elY + yAdjustment;

	if (!isOffBoundsAllowed.value) {
		trackerX = Math.max(rendererX, trackerX); // Left boundary
		trackerX = Math.min(
			rendererX + rendererWidth - contentsWidth,
			trackerX
		); // Right boundary
		trackerY = Math.max(MIN_TOP_PX, trackerY); // Top boundary
		trackerY = Math.min(bodyHeight - contentsHeight, trackerY); // Bottom boundary
	}

	rootStyle.value = {
		top: `${trackerY}px`,
		left: `${trackerX}px`,
		width: `${contentsWidth}px`,
		height: `${contentsHeight}px`,
	};
};

const triggerTrack = () => {
	let el: HTMLElement = document.querySelector(
		`.ComponentRenderer [data-streamsync-instance-path="${instancePath.value}"]`
	);
	scheduleNextTrigger();
	if (!el) return;
	const elStyle = getComputedStyle(el);
	if (!elStyle) return;
	if (elStyle.display == "contents") {
		el = el.querySelector("[data-streamsync-id]");
	}
	if (!el) return;
	trackElement(el);
};

const scheduleNextTrigger = () => {
	timerId.value = setTimeout(triggerTrack, REFRESH_INTERVAL_MS);
};

onMounted(async () => {
	await nextTick();
	triggerTrack();
});

onUnmounted(() => {
	clearTimeout(timerId.value);
});
</script>

<style scoped>
.BuilderInstanceTracker {
	position: absolute;
	transition: all 0.2s ease-in-out;
	pointer-events: none;
	z-index: 1;
}
</style>
