<template>
	<div
		ref="rootEl"
		class="WorkflowsWorkflow"
		:data-writer-unselectable="isUnselectable"
		@click="handleClick"
		@dragover="handleDragover"
		@drop="handleDrop"
		@mousemove="handleMousemove"
		@mousedown="handleMousedown"
		@mouseup="handleMouseup"
	>
		<div ref="nodeContainerEl" class="nodeContainer">
			<svg>
				<WorkflowArrow
					v-for="(arrow, arrowId) in arrows"
					:key="arrowId"
					:arrow="arrow"
					:is-selected="selectedArrow == arrowId"
					:is-engaged="
						selectedArrow == arrowId ||
						wfbm.getSelectedId() == arrow.fromNodeId ||
						wfbm.getSelectedId() == arrow.toNodeId
					"
					@click="handleArrowClick($event, arrowId)"
					@delete="handleDeleteClick($event, arrow)"
				></WorkflowArrow>
				<WorkflowArrow
					v-if="activeConnection?.liveArrow"
					key="liveArrow"
					:arrow="activeConnection.liveArrow"
					:is-selected="false"
					:is-engaged="true"
				></WorkflowArrow>
			</svg>
			<template v-for="node in nodes" :key="node.id">
				<component
					:is="renderProxiedComponent(node.id)"
					:style="{
						top: `${node.y - renderOffset.y}px`,
						left: `${node.x - renderOffset.x}px`,
						'border-color':
							activeConnection?.liveArrow?.toNodeId == node.id
								? activeConnection?.liveArrow?.color
								: undefined,
					}"
					@mousedown.stop="
						(ev: MouseEvent) => handleNodeMousedown(ev, node.id)
					"
					@out-mousedown="
						(outId: string) =>
							handleNodeOutMousedown(node.id, outId)
					"
				></component>
			</template>
		</div>
		<WdsButton class="runButton" variant="secondary" @click="handleRun">
			<i class="material-symbols-outlined">play_arrow</i>
			{{ isRunning ? "Running..." : "Run" }}</WdsButton
		>
		<WorkflowMiniMap
			v-if="nodeContainerEl"
			:node-container-el="nodeContainerEl"
			:render-offset="renderOffset"
			class="miniMap"
			@change-render-offset="handleChangeRenderOffset"
		></WorkflowMiniMap>
	</div>
</template>

<script lang="ts">
import { type Component, FieldType } from "@/writerTypes";
import WorkflowArrow from "./base/WorkflowArrow.vue";
import { watch } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WorkflowMiniMap from "./base/WorkflowMiniMap.vue";

const description =
	"A container component representing a single workflow within the application.";

export default {
	writer: {
		name: "Workflow",
		toolkit: "workflows",
		category: "Root",
		description,
		allowedChildrenTypes: ["*"],
		allowedParentTypes: ["workflows_root"],
		fields: {
			key: {
				name: "Workflow key",
				desc: "Unique identifier. It's needed to enable navigation to this Workflow.",
				type: FieldType.IdKey,
			},
		},
		previewField: "key",
	},
};

export type WorkflowArrowData = {
	x1: number;
	y1: number;
	x2: number;
	y2: number;
	color: string;
	fromNodeId: Component["id"];
	fromOutId: Component["outs"][number]["outId"];
	toNodeId?: Component["id"];
	isEngaged?: boolean;
};
</script>
<script setup lang="ts">
import { Ref, computed, inject, nextTick, onMounted, ref } from "vue";
import { useComponentActions } from "@/builder/useComponentActions";
import { useDragDropComponent } from "@/builder/useDragDropComponent";
import injectionKeys from "@/injectionKeys";
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);

const rootEl: Ref<HTMLElement | null> = ref(null);
const nodeContainerEl: Ref<HTMLElement | null> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const arrows: Ref<WorkflowArrowData[]> = ref([]);
const renderOffset = ref({ x: 0, y: 0 });
const isRunning = ref(false);
let clickOffset = { x: 0, y: 0 };
const selectedArrow = ref(null);
const instancePath = inject(injectionKeys.instancePath);
const workflowComponentId = inject(injectionKeys.componentId);

const nodes = computed(() =>
	wf.getComponents(workflowComponentId, { sortedByPosition: true }),
);

const { createAndInsertComponent, addOut, removeOut, changeCoordinates } =
	useComponentActions(wf, wfbm);
const { getComponentInfoFromDrag } = useDragDropComponent(wf);

const activeConnection: Ref<{
	fromNodeId: Component["id"];
	fromOutId: Component["outs"][number]["outId"];
	liveArrow?: WorkflowArrowData;
} | null> = ref(null);

const activeNodeMove: Ref<{
	nodeId: Component["id"];
	offset: { x: number; y: number };
	isPerfected: boolean;
} | null> = ref(null);

const activeCanvasMove: Ref<{
	offset: { x: number; y: number };
	isPerfected: boolean;
} | null> = ref(null);

function refreshArrows() {
	const a = [];

	nodes.value
		.filter((node) => node.outs?.length > 0)
		.forEach((node) => {
			const fromNodeId = node.id;
			node.outs.forEach((out) => {
				a.push(
					calculateArrow(
						fromNodeId,
						out.outId,
						undefined,
						out.toNodeId,
					),
				);
			});
		});
	arrows.value = a;
}

const isUnselectable = computed(() => {
	if (
		activeConnection.value === null &&
		!activeNodeMove.value?.isPerfected &&
		!activeCanvasMove.value?.isPerfected
	)
		return null;
	return true;
});

function handleClick() {
	selectedArrow.value = null;
}

async function handleRun() {
	if (isRunning.value) return;
	isRunning.value = true;
	await wf.forwardEvent(
		new CustomEvent("wf-builtin-run", {
			detail: {
				callback: () => {
					isRunning.value = false;
				},
			},
		}),
		instancePath,
		false,
	);
}

function handleNodeMousedown(ev: MouseEvent, nodeId: Component["id"]) {
	clearActiveOperations();
	const nodeEl = document.querySelector(`[data-writer-id="${nodeId}"]`);
	const nodeCBR = nodeEl.getBoundingClientRect();

	activeNodeMove.value = {
		nodeId,
		offset: {
			x: ev.pageX - nodeCBR.x,
			y: ev.pageY - nodeCBR.y,
		},
		isPerfected: false,
	};
}

function handleNodeOutMousedown(
	fromNodeId: Component["id"],
	fromOutId: string,
) {
	activeConnection.value = {
		fromNodeId,
		fromOutId,
	};
}

function getEmptyDragImage() {
	var img = new Image();
	img.src =
		"data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=";
	return img;
}

function handleDragstart(ev: DragEvent) {
	ev.dataTransfer.setDragImage(getEmptyDragImage(), 0, 0);
	clickOffset = getAdjustedCoordinates(ev);
}

function handleDrag(ev: DragEvent) {
	ev.preventDefault();
	const { x, y } = getAdjustedCoordinates(ev);
	if (x < 0 || y < 0) return;
	renderOffset.value.x = Math.max(
		0,
		renderOffset.value.x - (x - clickOffset.x),
	);
	renderOffset.value.y = Math.max(
		0,
		renderOffset.value.y - (y - clickOffset.y),
	);
	refreshArrows();
}

function handleDragover(ev: DragEvent) {
	ev.preventDefault();
	ev.stopPropagation();
}

function getAdjustedCoordinates(ev: MouseEvent) {
	const canvasCBR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasCBR.x + renderOffset.value.x;
	const y = ev.pageY - canvasCBR.y + renderOffset.value.y;
	return { x, y };
}

function handleDrop(ev: DragEvent) {
	ev.preventDefault();
	ev.stopPropagation();
	const dropInfo = getComponentInfoFromDrag(ev);

	if (!dropInfo) return;
	const { draggedType, draggedId } = dropInfo;
	if (draggedId) return;

	const { x, y } = getAdjustedCoordinates(ev);
	if (x < 0 || y < 0) return;

	createNode(draggedType, x, y);
}

function handleArrowClick(ev: MouseEvent, arrowId: number) {
	if (selectedArrow.value == arrowId) {
		selectedArrow.value = null;
		return;
	}
	ev.stopPropagation();
	selectedArrow.value = arrowId;
	wfbm.setSelection(null);
}

async function handleDeleteClick(ev: MouseEvent, arrow: WorkflowArrowData) {
	if (!arrow.toNodeId) return;
	const out = {
		outId: arrow.fromOutId,
		toNodeId: arrow.toNodeId,
	};
	removeOut(arrow.fromNodeId, out);
}

function handleNodeDragStart(ev: DragEvent) {
	ev.stopPropagation();
	ev.dataTransfer.setDragImage(getEmptyDragImage(), 0, 0);
	clickOffset = {
		x: ev.offsetX,
		y: ev.offsetY,
	};
}

function handleNodeDrag(ev: DragEvent, componentId: Component["id"]) {
	ev.preventDefault();
	ev.stopPropagation();
	const { x, y } = getAdjustedCoordinates(ev);
	if (x < 0 || y < 0) return;

	const component = wf.getComponentById(componentId);

	const newX = x - clickOffset.x;
	const newY = y - clickOffset.y;

	if (component.x == newX && component.y == newY) return;

	component.x = newX;
	component.y = newY;

	setTimeout(() => {
		// Debouncing
		if (component.x !== newX) return;
		if (component.y !== newY) return;
		changeCoordinates(componentId, newX, newY);
	}, 200);
}

function calculateArrow(
	fromNodeId: Component["id"],
	fromOutId: string,
	toCoordinates?: { x: number; y: number },
	toNodeId?: Component["id"],
): WorkflowArrowData {
	let x1: number, y1: number, x2: number, y2: number;
	const canvasCBR = rootEl.value?.getBoundingClientRect();
	if (!canvasCBR) {
		return;
	}
	x2 = toCoordinates?.x - canvasCBR.x;
	y2 = toCoordinates?.y - canvasCBR.y;
	const fromEl = document.querySelector(
		`[data-writer-id="${fromNodeId}"] [data-writer-socket-id="${fromOutId}"]`,
	);
	if (!fromEl) return;
	const fromCBR = fromEl.getBoundingClientRect();
	x1 = fromCBR.x - canvasCBR.x + fromCBR.width / 2;
	y1 = fromCBR.y - canvasCBR.y + fromCBR.height / 2;
	if (!fromEl) return;
	if (typeof toNodeId !== "undefined") {
		const toEl = document.querySelector(`[data-writer-id="${toNodeId}"]`);
		const toCBR = toEl.getBoundingClientRect();
		x2 = toCBR.x - canvasCBR.x;
		y2 = toCBR.y - canvasCBR.y + toCBR.height / 2;
	}

	return {
		x1,
		y1,
		x2,
		y2,
		color: getComputedStyle(fromEl).backgroundColor,
		fromNodeId,
		fromOutId,
		toNodeId,
	};
}

function getHoveredNodeId(ev: MouseEvent) {
	const targetEl = ev.target as HTMLElement;
	const toNodeEl = targetEl.closest(
		".WorkflowsWorkflow [data-writer-id]",
	) as HTMLElement;
	return toNodeEl?.dataset.writerId;
}

function refreshLiveArrow(ev: MouseEvent) {
	let toCoordinates: { x: number; y: number }, toNodeId: Component["id"];

	toNodeId = getHoveredNodeId(ev);
	if (typeof toNodeId == "undefined") {
		toCoordinates = { x: ev.pageX, y: ev.pageY };
	}
	const { fromNodeId, fromOutId } = activeConnection.value;
	if (toNodeId == fromNodeId) return;

	activeConnection.value.liveArrow = calculateArrow(
		fromNodeId,
		fromOutId,
		toCoordinates,
		toNodeId,
	);
}

function clearActiveOperations() {
	activeCanvasMove.value = null;
	activeConnection.value = null;
	activeNodeMove.value = null;
}

function moveNode(ev: MouseEvent) {
	const { nodeId, offset } = activeNodeMove.value;
	activeNodeMove.value.isPerfected = true;
	const component = wf.getComponentById(nodeId);
	const { x, y } = getAdjustedCoordinates(ev);

	const newX = x - offset.x;
	const newY = y - offset.y;

	if (component.x == newX && component.y == newY) return;

	component.x = newX;
	component.y = newY;
}

async function moveCanvas(ev: MouseEvent) {
	const canvasCBR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasCBR.x;
	const y = ev.pageY - canvasCBR.y;
	const { x: prevX, y: prevY } = activeCanvasMove.value.offset;
	activeCanvasMove.value.isPerfected = true;

	renderOffset.value = {
		x: Math.max(0, renderOffset.value.x + (prevX - x) * 1),
		y: Math.max(0, renderOffset.value.y + (prevY - y) * 1),
	};
	activeCanvasMove.value.offset = { x, y };
	await nextTick();
	refreshArrows();
}

function handleMousemove(ev: MouseEvent) {
	if (ev.buttons != 1) return;

	if (activeConnection.value) {
		refreshLiveArrow(ev);
		return;
	}
	if (activeNodeMove.value) {
		moveNode(ev);
		return;
	}
	if (activeCanvasMove.value) {
		moveCanvas(ev);
		return;
	}
}

function handleMousedown(ev: MouseEvent) {
	clearActiveOperations();
	if (ev.buttons != 1) return;

	const canvasCBR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasCBR.x;
	const y = ev.pageY - canvasCBR.y;

	activeCanvasMove.value = {
		offset: { x, y },
		isPerfected: false,
	};
}

async function handleMouseup(ev: MouseEvent) {
	if (activeConnection.value === null) {
		return;
	}
	const hoveredId = getHoveredNodeId(ev);
	if (!hoveredId) {
		activeConnection.value = null;
		return;
	}
	const { fromNodeId, fromOutId } = activeConnection.value;
	if (fromNodeId == hoveredId) {
		activeConnection.value = null;
		return;
	}

	addOut(activeConnection.value.fromNodeId, {
		toNodeId: hoveredId,
		outId: fromOutId,
	});
}

async function createNode(type: string, x: number, y: number) {
	createAndInsertComponent(type, workflowComponentId, undefined, {
		x: Math.floor(x),
		y: Math.floor(y),
	});
}

async function findAndCenterBlock(componentId: Component["id"]) {
	const el = rootEl.value.querySelector(`[data-writer-id="${componentId}"]`);
	const canvasCBR = rootEl.value?.getBoundingClientRect();
	if (!el || !canvasCBR) return;
	const { width, height } = el.getBoundingClientRect();
	const component = wf.getComponentById(componentId);
	if (!component) return;
	renderOffset.value = {
		x: Math.max(0, component.x - canvasCBR.width / 2 + width / 2),
		y: Math.max(0, component.y - canvasCBR.height / 2 + height / 2),
	};
	await nextTick();
	refreshArrows();
}

async function handleChangeRenderOffset(payload) {
	renderOffset.value = {
		x: payload.x,
		y: payload.y,
	};
	await nextTick();
	refreshArrows();
}

watch(
	() => wfbm.getSelection(),
	(newSelection) => {
		if (!newSelection) return;
		selectedArrow.value = null;
		if (!wf.isChildOf(workflowComponentId, newSelection.componentId))
			return;
		if (newSelection.source !== "click") {
			findAndCenterBlock(newSelection.componentId);
		}
	},
);

watch(
	nodes,
	async () => {
		// Refresh arrows

		await nextTick();
		refreshArrows();
	},
	{ deep: true },
);

onMounted(async () => {
	await nextTick();
	refreshArrows();
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.WorkflowsWorkflow {
	display: flex;
	width: 100%;
	min-height: 100%;
	background: var(--builderSubtleSeparatorColor);
	flex: 1 0 auto;
	flex-direction: row;
	align-items: stretch;
	position: relative;
	overflow: hidden;
}

button.runButton {
	position: absolute;
	right: 32px;
	top: 32px;
}

.component.WorkflowsWorkflow.selected {
	background: var(--builderSubtleSeparatorColor);
}

.miniMap {
	position: absolute;
	bottom: 32px;
	left: 32px;
}

.nodeContainer {
	position: absolute;
	top: 0;
	left: 0;
	overflow: hidden;
	width: 100%;
	height: 100%;
}

svg {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}
</style>
