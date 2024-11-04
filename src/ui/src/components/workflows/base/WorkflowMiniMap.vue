<template>
	<div
		ref="rootEl"
		class="WorkflowMiniMap"
		data-writer-unselectable="true"
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
			:class="{ selected: wfbm.getSelectedId() == miniNode.id }"
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
import { inject, nextTick, onMounted, onUnmounted, ref } from "vue";

const wfbm = inject(injectionKeys.builderManager);
const rootEl = ref(null);
const emit = defineEmits(["changeRenderOffset"]);
const resizeObserver = new ResizeObserver(render);
const mutationObserver = new MutationObserver(render);

const scale = ref(0.2);

const miniMap = ref({
	width: 166,
	height: 100,
});

const selector = ref({
	width: 166,
	height: 100,
	top: 0,
	left: 0,
	isDisplayed: false,
});

const selectedArea = ref({
	width: 166,
	height: 100,
	top: 0,
	left: 0,
});

const props = defineProps<{
	nodeContainerEl: HTMLElement;
	renderOffset: { x: number; y: number };
}>();
const miniNodes = ref([]);

function render() {
	if (!props.nodeContainerEl) return;

	const nodeEls = Array.from(
		props.nodeContainerEl.querySelectorAll("[data-writer-id]"),
	) as HTMLElement[];

	const cbr = props.nodeContainerEl.getBoundingClientRect();
	let maxX = 0,
		maxY = 0;

	miniNodes.value = nodeEls.map((nodeEl) => {
		const nodeCbr = nodeEl.getBoundingClientRect();
		maxX = Math.max(maxX, nodeCbr.right + props.renderOffset.x - cbr.left);
		maxY = Math.max(maxY, nodeCbr.bottom + props.renderOffset.y - cbr.top);
		return {
			id: nodeEl.dataset.writerId,
			width: nodeCbr.width,
			height: nodeCbr.height,
			top: nodeCbr.top + props.renderOffset.y - cbr.top,
			left: nodeCbr.left + props.renderOffset.x - cbr.left,
		};
	});

	miniMap.value = {
		width: cbr.width / 7,
		height: ((cbr.height / cbr.width) * cbr.width) / 7,
	};

	scale.value = Math.min(
		miniMap.value.width / (cbr.width + 300),
		miniMap.value.height / (cbr.height + 300),
		miniMap.value.width / (maxX + 300),
		miniMap.value.height / (maxY + 300),
		miniMap.value.width / (props.renderOffset.x + cbr.width),
		miniMap.value.height / (props.renderOffset.y + cbr.height),
	);

	selectedArea.value = {
		top: props.renderOffset.y,
		left: props.renderOffset.x,
		width: cbr.width,
		height: cbr.height,
	};

	selector.value = {
		...selectedArea.value,
		isDisplayed: selector.value.isDisplayed,
	};
}

function handleMousemove(ev: MouseEvent) {
	const cbr = props.nodeContainerEl.getBoundingClientRect();
	const rootElCbr = rootEl.value.getBoundingClientRect();
	selector.value = {
		...selector.value,
		top: Math.min(
			Math.max(
				0,
				(ev.pageY - rootElCbr.top) * (1 / scale.value) - cbr.height / 2,
			),
			rootElCbr.height * (1 / scale.value) - cbr.height,
		),
		left: Math.min(
			Math.max(
				0,
				(ev.pageX - rootElCbr.left) * (1 / scale.value) - cbr.width / 2,
			),
			rootElCbr.width * (1 / scale.value) - cbr.width,
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
		x: selector.value.left,
		y: selector.value.top,
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
	border-radius: 4px;
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
	background: #6985ff;
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
	border: 1px solid #6985ff;
	border-radius: 4px;
	pointer-events: none;
	display: v-bind("selector.isDisplayed ? '' : 'none'");
}
</style>
