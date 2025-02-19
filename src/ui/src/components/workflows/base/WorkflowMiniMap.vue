<template>
	<div
		ref="rootEl"
		class="WorkflowMiniMap"
		@mouseenter="handleMouseenter"
		@mouseleave="handleMouseleave"
		@mousemove="handleMousemove"
		@click="handleClick"
	>
		<div
			class="selectedArea"
			:style="{
				top: `${selectedArea.top * scale}px`,
				left: `${selectedArea.left * scale}px`,
				width: `${selectedArea.width * scale}px`,
				height: `${selectedArea.height * scale}px`,
			}"
		></div>
		<div
			class="selector"
			:style="{
				top: `${selector.top * scale}px`,
				left: `${selector.left * scale}px`,
				width: `${selector.width * scale}px`,
				height: `${selector.height * scale}px`,
			}"
		></div>
		<div
			v-for="miniNode in miniNodes"
			:key="miniNode.id"
			class="node"
			:class="{ selected: wfbm.isComponentIdSelected(miniNode.id) }"
			:style="{
				top: `${miniNode.top * scale}px`,
				left: `${miniNode.left * scale}px`,
				width: `${miniNode.width * scale}px`,
				height: `${miniNode.height * scale}px`,
			}"
		></div>
	</div>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import {
	inject,
	nextTick,
	onMounted,
	onUnmounted,
	ref,
	useTemplateRef,
} from "vue";

const wfbm = inject(injectionKeys.builderManager);
const rootEl = useTemplateRef("rootEl");
const emit = defineEmits(["changeRenderOffset"]);
const resizeObserver = new ResizeObserver(render);
const mutationObserver = new MutationObserver(render);

const scale = ref(0.2);

const miniMap = ref({
	width: 166,
	height: 100,
});

const selector = ref({
	width: 260,
	height: 1,
	top: 0,
	left: 0,
	isDisplayed: false,
});

const selectedArea = ref({
	width: 1,
	height: 1,
	top: 0,
	left: 0,
});

const props = defineProps<{
	nodeContainerEl: HTMLElement;
	renderOffset: { x: number; y: number };
	zoomLevel: number;
}>();
const miniNodes = ref([]);

function render() {
	if (!props.nodeContainerEl) return;

	const nodeEls = Array.from(
		props.nodeContainerEl.querySelectorAll("[data-writer-id]"),
	) as HTMLElement[];

	const nodeContainerBCR = props.nodeContainerEl.getBoundingClientRect();
	let maxX = 0,
		maxY = 0;

	miniNodes.value = nodeEls.map((nodeEl) => {
		const nodeBCR = nodeEl.getBoundingClientRect();
		maxX = Math.max(
			maxX,
			nodeBCR.right +
				props.renderOffset.x * props.zoomLevel -
				nodeContainerBCR.left,
		);
		maxY = Math.max(
			maxY,
			nodeBCR.bottom +
				props.renderOffset.y * props.zoomLevel -
				nodeContainerBCR.top,
		);
		return {
			id: nodeEl.dataset.writerId,
			width: nodeBCR.width,
			height: nodeBCR.height,
			top:
				nodeBCR.top +
				props.renderOffset.y * props.zoomLevel -
				nodeContainerBCR.top,
			left:
				nodeBCR.left +
				props.renderOffset.x * props.zoomLevel -
				nodeContainerBCR.left,
		};
	});

	miniMap.value = {
		width: 260,
		height:
			((nodeContainerBCR.height / nodeContainerBCR.width) *
				nodeContainerBCR.width) /
			7,
	};

	scale.value = Math.min(
		miniMap.value.width / (nodeContainerBCR.width + 300),
		miniMap.value.height / (nodeContainerBCR.height + 300),
		miniMap.value.width / (maxX + 300),
		miniMap.value.height / (maxY + 300),
		miniMap.value.width /
			(props.renderOffset.x * props.zoomLevel + nodeContainerBCR.width),
		miniMap.value.height /
			(props.renderOffset.y * props.zoomLevel + nodeContainerBCR.height),
	);

	selectedArea.value = {
		top: props.renderOffset.y * props.zoomLevel,
		left: props.renderOffset.x * props.zoomLevel,
		width: nodeContainerBCR.width,
		height: nodeContainerBCR.height,
	};

	selector.value = {
		...selectedArea.value,
		isDisplayed: selector.value.isDisplayed,
	};
}

function handleMousemove(ev: MouseEvent) {
	const nodeContainerBCR = props.nodeContainerEl.getBoundingClientRect();
	const rootBCR = rootEl.value.getBoundingClientRect();
	selector.value = {
		...selector.value,
		top: Math.min(
			Math.max(
				0,
				(ev.pageY - rootBCR.top) * (1 / scale.value) -
					nodeContainerBCR.height / 2,
			),
			rootBCR.height * (1 / scale.value) - nodeContainerBCR.height,
		),
		left: Math.min(
			Math.max(
				0,
				(ev.pageX - rootBCR.left) * (1 / scale.value) -
					nodeContainerBCR.width / 2,
			),
			rootBCR.width * (1 / scale.value) - nodeContainerBCR.width,
		),
	};
}

function handleMouseenter() {
	selector.value.isDisplayed = true;
}

function handleMouseleave() {
	selector.value.isDisplayed = false;
}

function handleClick(ev: MouseEvent) {
	ev.stopPropagation();
	wfbm.setSelection(null);
	emit("changeRenderOffset", {
		x: selector.value.left * (1 / props.zoomLevel),
		y: selector.value.top * (1 / props.zoomLevel),
	});
}

onMounted(async () => {
	resizeObserver.observe(props.nodeContainerEl);
	mutationObserver.observe(props.nodeContainerEl, {
		subtree: true,
		childList: true,
		attributes: true,
		attributeFilter: ["style"],
	});
	await nextTick();
	render();
});

onUnmounted(() => {
	resizeObserver.disconnect();
	mutationObserver.disconnect();
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.WorkflowMiniMap {
	width: v-bind("`${miniMap.width}px`");
	height: v-bind("`${miniMap.height}px`");
	background: var(--builderSeparatorColor);
	position: relative;
	overflow: hidden;
}

.node {
	position: absolute;
	top: 4px;
	left: 4px;
	width: 10px;
	height: 5px;
	background: white;
	pointer-events: none;
}

.node.selected {
	background: var(--wdsColorBlue4);
}

.selectedArea {
	position: absolute;
	top: 0px;
	left: 0px;
	background: rgba(0, 0, 0, 0.05);
	pointer-events: none;
	border-radius: 4px;
}

.selector {
	position: absolute;
	top: 0px;
	left: 0px;
	border: 1px solid var(--wdsColorBlue4);
	border-radius: 4px;
	pointer-events: none;
	display: v-bind("selector.isDisplayed ? '' : 'none'");
}
</style>
