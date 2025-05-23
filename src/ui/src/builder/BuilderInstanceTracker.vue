<template>
	<div ref="rootEl" class="BuilderInstanceTracker" :style="rootStyle">
		<slot></slot>
	</div>
</template>
<script setup lang="ts">
import { useAbortController } from "@/composables/useAbortController";
import {
	CSSProperties,
	onMounted,
	onUnmounted,
	shallowRef,
	toRefs,
	useTemplateRef,
} from "vue";

const REFRESH_INTERVAL_MS = 200;

interface Props {
	instancePath: string;
	matchSize?: boolean;
	verticalOffsetPixels?: number;
	isOffBoundsAllowed?: boolean;
	preventSettingsBarOverlap?: boolean;
}
const props = defineProps<Props>();
const {
	instancePath,
	matchSize,
	verticalOffsetPixels,
	isOffBoundsAllowed,
	preventSettingsBarOverlap,
} = toRefs(props);

type RootStyle = Partial<
	Pick<CSSProperties, "top" | "left" | "width" | "height">
>;

const rootStyle = shallowRef<RootStyle>({});
let timerId = 0;
const rootEl = useTemplateRef("rootEl");
const MIN_TOP_PX = 36;

function trackElement(el: Element) {
	const rendererEl = document.querySelector(".ComponentRenderer");
	const { top: elY, left: elX } = el.getBoundingClientRect();
	const { clientHeight: bodyHeight } = document.body;
	const { clientWidth: rendererWidth } = rendererEl;
	const { left: rendererX } = rendererEl.getBoundingClientRect();
	const settingsEl = document.querySelector(".BuilderSettings");
	const { left: settingsLeft } = settingsEl?.getBoundingClientRect() || {
		left: Infinity,
	};
	let { clientHeight: contentsHeight, clientWidth: contentsWidth } =
		(matchSize?.value ? el : rootEl.value) ?? {};

	if (contentsHeight === undefined || contentsWidth === undefined) return;

	let yAdjustment = verticalOffsetPixels?.value
		? verticalOffsetPixels.value
		: 0;

	let trackerX = elX;
	let trackerY = elY + yAdjustment;

	if (!isOffBoundsAllowed.value) {
		trackerX = Math.max(rendererX, trackerX); // Left boundary
		trackerX = Math.min(
			rendererX + rendererWidth - contentsWidth,
			trackerX,
		); // Right boundary
		trackerY = Math.max(MIN_TOP_PX, trackerY); // Top boundary
		trackerY = Math.min(bodyHeight - contentsHeight, trackerY); // Bottom boundary
	}

	if (preventSettingsBarOverlap.value) {
		let correction = 0;
		if (trackerX + contentsWidth > settingsLeft) {
			correction = Math.max(trackerX - (settingsLeft - contentsWidth), 0);
		}

		trackerX -= correction;
	}

	rootStyle.value = {
		top: `${trackerY}px`,
		left: `${trackerX}px`,
		width: `${contentsWidth}px`,
		height: `${contentsHeight}px`,
	};
}

function triggerTrack() {
	let el = document.querySelector(
		`.ComponentRenderer [data-writer-instance-path="${instancePath.value}"]`,
	);
	if (!el) return;
	const elStyle = getComputedStyle(el);
	if (!elStyle) return;
	if (elStyle.display == "contents") {
		el = el.querySelector("[data-writer-id]");
	}
	if (!el) return;
	trackElement(el);
}

function scheduleNextTrigger() {
	timerId = requestAnimationFrame(async () => {
		triggerTrack();
		if (abort.signal.aborted) return;
		await new Promise((res) => setTimeout(res, REFRESH_INTERVAL_MS));
		scheduleNextTrigger();
	});
}

const abort = useAbortController();

defineExpose({
	refresh: triggerTrack,
});

onMounted(async () => {
	window.addEventListener("scroll", triggerTrack, { signal: abort.signal });
	scheduleNextTrigger();
});

onUnmounted(() => {
	cancelAnimationFrame(timerId);
});
</script>

<style scoped>
.BuilderInstanceTracker {
	position: absolute;
	pointer-events: none;
	z-index: 1;
}
</style>
