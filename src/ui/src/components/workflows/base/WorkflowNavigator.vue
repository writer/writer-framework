<template>
	<div
		ref="rootEl"
		data-writer-unselectable="true"
		class="WorkflowNavigator"
		@keydown="handleKeydown"
	>
		<WorkflowMiniMap
			v-if="nodeContainerEl && isMiniMapShown"
			:node-container-el="nodeContainerEl"
			:render-offset="renderOffset"
			:zoom-level="zoomLevel"
			class="miniMap"
			@change-render-offset="handleRenderOffsetChange"
		></WorkflowMiniMap>
		<div class="bar">
			<div class="zoomer">
				<WdsButton
					variant="neutral"
					size="unpadded"
					:data-writer-tooltip="
						zoomLevel > ZOOM_SETTINGS.minLevel
							? `Zoom out (${getModifierKeyName()}-)`
							: `Can't zoom further`
					"
					data-writer-tooltip-placement="left"
					@click="handleZoomOutClick"
				>
					<i class="material-symbols-outlined">remove</i>
				</WdsButton>
				<WdsTextInput
					v-model="zoomLevelAsText"
					class="zoomLevelInput"
					@keydown="handleZoomLevelInputKeydown"
					@change="handleZoomLevelInputChange"
				></WdsTextInput>
				<WdsButton
					variant="neutral"
					size="unpadded"
					:data-writer-tooltip="
						zoomLevel < ZOOM_SETTINGS.maxLevel
							? `Zoom in (${getModifierKeyName()}+)`
							: `Can't zoom further`
					"
					data-writer-tooltip-placement="right"
					@click="handleZoomInClick"
				>
					<i class="material-symbols-outlined">add</i>
				</WdsButton>
				<WdsButton
					variant="neutral"
					size="unpadded"
					data-writer-tooltip="Reset zoom"
					data-writer-tooltip-placement="right"
					@click="handleResetZoom"
				>
					<i class="material-symbols-outlined">undo</i>
				</WdsButton>
			</div>
			<div class="miniMapCollapser">
				<WdsButton
					variant="neutral"
					size="unpadded"
					:data-writer-tooltip="
						isMiniMapShown ? `Close minimap` : `Open minimap`
					"
					data-writer-tooltip-placement="right"
					@click="toggleMiniMap"
				>
					<i class="material-symbols-outlined">close_fullscreen</i>
				</WdsButton>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, toRefs, watch } from "vue";
import WorkflowMiniMap from "./WorkflowMiniMap.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";

import { ZOOM_SETTINGS } from "../WorkflowsWorkflow.vue";
import { getModifierKeyName, isModifierKeyActive } from "@/core/detectPlatform";

const INPUT_KEYDOWN_STEP = 0.01;
const ZOOM_INOUT_BUTTON_STEP = 0.2;

const props = defineProps<{
	nodeContainerEl: HTMLElement;
	renderOffset: { x: number; y: number };
	zoomLevel: number;
}>();

const { zoomLevel } = toRefs(props);

const rootEl = ref(null);
const emit = defineEmits([
	"changeRenderOffset",
	"changeZoomLevel",
	"resetZoom",
]);
const isMiniMapShown = ref(true);
const zoomLevelAsText = ref<string>(
	convertNumericZoomLevelToText(zoomLevel.value),
);

function convertNumericZoomLevelToText(zoomLevel: number) {
	return `${Math.floor(zoomLevel * 100)}%`;
}

function toggleMiniMap() {
	isMiniMapShown.value = !isMiniMapShown.value;
}

function handleRenderOffsetChange(offset: typeof props.renderOffset) {
	emit("changeRenderOffset", offset);
}

function handleZoomInClick() {
	const newZoomLevel = zoomLevel.value + ZOOM_INOUT_BUTTON_STEP;
	emit("changeZoomLevel", newZoomLevel);
}

function handleZoomOutClick() {
	const newZoomLevel = zoomLevel.value - ZOOM_INOUT_BUTTON_STEP;
	emit("changeZoomLevel", newZoomLevel);
}

function handleZoomLevelInputKeydown(ev: KeyboardEvent) {
	const key = ev.key;
	let newZoomLevel = zoomLevel.value;
	if (key == "ArrowUp") {
		newZoomLevel += INPUT_KEYDOWN_STEP;
	} else if (key == "ArrowDown") {
		newZoomLevel -= INPUT_KEYDOWN_STEP;
	} else {
		return;
	}
	emit("changeZoomLevel", newZoomLevel);
}

function handleZoomLevelInputChange(ev: InputEvent) {
	const newText = (ev.target as HTMLInputElement)?.value;
	let newZoomLevel = parseInt(newText) / 100;
	if (isNaN(newZoomLevel)) {
		newZoomLevel = 1;
	}
	zoomLevelAsText.value = convertNumericZoomLevelToText(newZoomLevel);
	emit("changeZoomLevel", newZoomLevel);
}

function handleResetZoom() {
	emit("resetZoom");
}

watch(zoomLevel, (newZoomLevel) => {
	zoomLevelAsText.value = convertNumericZoomLevelToText(newZoomLevel);
});

function handleKeydown(ev: KeyboardEvent) {
	if (isModifierKeyActive(ev) === false) return;

	let newZoomLevel = zoomLevel.value;
	if (ev.key == "+" || ev.key == "=") {
		ev.preventDefault();
		newZoomLevel += ZOOM_INOUT_BUTTON_STEP;
	} else if (ev.key == "-") {
		ev.preventDefault();
		newZoomLevel -= ZOOM_INOUT_BUTTON_STEP;
	} else {
		return;
	}
	emit("changeZoomLevel", newZoomLevel);
}

onMounted(() => {
	document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
	document.removeEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.WorkflowNavigator {
	overflow: hidden;
	color: var(--builderSecondaryTextColor);
	border: 1px solid var(--builderSeparatorColor);
	width: 230px;
}

.bar {
	display: flex;
	background: var(--builderBackgroundColor);
}

.zoomer {
	flex: 1 0 auto;
	display: flex;
	padding: 6px 12px 6px 12px;
	gap: 12px;
	align-items: center;
}

.zoomer .zoomLevelInput {
	font-size: 12px;
	padding: 4px;
	width: 60px;
	text-align: center;
}

.miniMapCollapser {
	min-height: 36px;
	min-width: 40px;
	flex: 0 0 40px;
	display: flex;
	border-left: 1px solid var(--builderSeparatorColor);
	align-items: center;
	justify-content: center;
}
</style>
