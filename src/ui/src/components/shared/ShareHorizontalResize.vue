<template>
	<div ref="root" class="ShareHorizontalResize" :style="style">
		<div class="ShareHorizontalResize__left">
			<slot name="left" />
		</div>
		<hr
			class="ShareHorizontalResize__divider"
			@mousedown.prevent="handleMouseDown"
		/>
		<div class="ShareHorizontalResize__right">
			<slot name="right" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, CSSProperties, ref, useTemplateRef } from "vue";

const props = defineProps({
	initialLeftSize: { type: Number, required: true },
});
const root = useTemplateRef("root");

let leftSize = ref(props.initialLeftSize);
const style = computed<CSSProperties>(() => ({
	gridTemplateColumns: `${leftSize.value}px 1px minmax(0, 100%)`,
}));

function handleMouseDown() {
	if (!root.value) return;
	document.addEventListener("mousemove", onMouseMove);
	document.addEventListener("mouseup", onMouseUp);

	const rootBoundingRect = root.value.getBoundingClientRect();

	function onMouseMove(event: MouseEvent) {
		leftSize.value = event.x - rootBoundingRect.left;
	}

	function onMouseUp() {
		document.removeEventListener("mouseup", onMouseUp);
		document.removeEventListener("mousemove", onMouseMove);
	}
}
</script>

<style scoped>
.ShareHorizontalResize {
	display: grid;
	height: 100%;
}

.ShareHorizontalResize__divider {
	border: none;
	background-color: var(--builderSeparatorColor);
	height: 100%;
	cursor: ew-resize;
}
</style>
