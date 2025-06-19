<template>
	<div ref="root" class="ShareResizeVertical" :style="style">
		<div class="ShareResizeVertical__top">
			<slot name="top" />
		</div>
		<div class="ShareResizeVertical__divider">
			<div
				v-if="!disabled"
				class="ShareResizeVertical__divider__hand"
				@mousedown.prevent="handleMouseDown"
			></div>
		</div>
		<div class="ShareResizeVertical__bottom">
			<slot name="bottom" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { useAbortController } from "@/composables/useAbortController";
import {
	computed,
	CSSProperties,
	ref,
	toRef,
	useTemplateRef,
	watch,
} from "vue";

const props = defineProps({
	initialBottomSize: {
		type: Number,
		required: true,
	},
	disabled: {
		type: Boolean,
		required: false,
	},
});

const root = useTemplateRef("root");
const abort = useAbortController();

const initialBottomSize = toRef(props, "initialBottomSize");

let bottomSize = ref(initialBottomSize.value);
watch(initialBottomSize, () => (bottomSize.value = initialBottomSize.value));

const style = computed<CSSProperties>(() => ({
	gridTemplateRows: `minmax(0px, 1fr) 1px ${bottomSize.value}px`,
}));

function handleMouseDown() {
	if (!root.value) return;
	document.addEventListener("mousemove", onMouseMove, {
		signal: abort.signal,
	});
	document.addEventListener("mouseup", onMouseUp, { signal: abort.signal });

	const rootBoundingRect = root.value.getBoundingClientRect();

	function onMouseMove(event: MouseEvent) {
		bottomSize.value = rootBoundingRect.bottom - event.clientY;
	}

	function onMouseUp() {
		document.removeEventListener("mouseup", onMouseUp);
		document.removeEventListener("mousemove", onMouseMove);
	}
}
</script>

<style scoped>
.ShareResizeVertical {
	display: grid;
	height: 100%;
}

.ShareResizeVertical__divider {
	position: relative;
	background-color: transparent;
}
.ShareResizeVertical__divider__hand {
	cursor: ns-resize;
	background-color: var(--wdsColorGray3);
	width: 40px;
	height: 7px;
	position: absolute;
	left: calc(50% - 20px);
	top: -2px;
	border-radius: 4px;
}
</style>
