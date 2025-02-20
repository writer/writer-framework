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
						wfbm.isComponentIdSelected(arrow.fromNodeId) ||
						wfbm.isComponentIdSelected(arrow.toNodeId)
					"
					@click="handleArrowClick($event, arrowId)"
					@delete="handleArrowDeleteClick(arrow)"
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
					:is="renderProxiedComponent(node.id, 0)"
					:style="{
						top: `${(temporaryNodeCoordinates?.[node.id]?.y ?? node.y) - renderOffset.y}px`,
						left: `${(temporaryNodeCoordinates?.[node.id]?.x ?? node.x) - renderOffset.x}px`,
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
		<div class="workflowsToolbar">
			<WdsButton
				variant="secondary"
				size="small"
				:data-writer-unselectable="true"
				data-automation-action="run-workflow"
				@click="handleRun"
			>
				<i class="material-symbols-outlined">play_arrow</i>
				{{ isRunning ? "Running..." : "Run workflow" }}
			</WdsButton>
		</div>
		<WorkflowNavigator
			v-if="nodeContainerEl"
			:node-container-el="nodeContainerEl"
			:render-offset="renderOffset"
			:zoom-level="zoomLevel"
			class="navigator"
			@auto-arrange="handleAutoArrange"
			@change-render-offset="handleChangeRenderOffset"
			@change-zoom-level="handleChangeZoomLevel"
			@reset-zoom="resetZoom"
		></WorkflowNavigator>
	</div>
</template>

<script lang="ts">
import { type Component, FieldType } from "@/writerTypes";
import WorkflowArrow from "./base/WorkflowArrow.vue";
import { watch } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WorkflowNavigator from "./base/WorkflowNavigator.vue";
import { isModifierKeyActive } from "@/core/detectPlatform";

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

export const ZOOM_SETTINGS = {
	minLevel: 0.2,
	maxLevel: 1,
	step: 0.25,
	initialLevel: 1,
};
</script>
<script setup lang="ts">
import {
	Ref,
	computed,
	inject,
	nextTick,
	onMounted,
	onUnmounted,
	ref,
	shallowRef,
	useTemplateRef,
} from "vue";
import { useComponentActions } from "@/builder/useComponentActions";
import { useDragDropComponent } from "@/builder/useDragDropComponent";
import injectionKeys from "@/injectionKeys";

const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);
const workflowComponentId = inject(injectionKeys.componentId);

const rootEl = useTemplateRef("rootEl");
const nodeContainerEl = useTemplateRef("nodeContainerEl");
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const arrows: Ref<WorkflowArrowData[]> = ref([]);
const renderOffset = shallowRef({ x: 0, y: 0 });
const isRunning = ref(false);
const selectedArrow = ref(null);
const zoomLevel = ref(ZOOM_SETTINGS.initialLevel);
const arrowRefresherObserver = new MutationObserver(refreshArrows);
const temporaryNodeCoordinates = shallowRef<
	Record<Component["id"], { x: number; y: number }>
>({});

const AUTOARRANGE_ROW_GAP_PX = 96;
const AUTOARRANGE_COLUMN_GAP_PX = 128;

const nodes = computed(() =>
	wf.getComponents(workflowComponentId, { sortedByPosition: true }),
);

const {
	createAndInsertComponent,
	addOut,
	removeOut,
	changeCoordinatesMultiple,
} = useComponentActions(wf, wfbm);
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
	const newArrows = [];
	nodes.value
		.filter((node) => node.outs?.length > 0)
		.forEach((node) => {
			const fromNodeId = node.id;
			node.outs.forEach((out) => {
				const arrow = calculateArrow(
					fromNodeId,
					out.outId,
					undefined,
					out.toNodeId,
				);
				if (!arrow) return;
				newArrows.push(arrow);
			});
		});
	arrows.value = newArrows;
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

function organizeNodesInColumns() {
	const columns: Map<number, Set<Component>> = new Map();

	function scan(node: Component, layer: number) {
		columns.forEach((column) => {
			if (column.has(node)) {
				column.delete(node);
			}
		});
		if (!columns.has(layer)) {
			columns.set(layer, new Set());
		}
		const column = columns.get(layer);
		column.add(node);
		node.outs?.forEach((out) => {
			const outNode = wf.getComponentById(out.toNodeId);
			scan(outNode, layer + 1);
		});
	}

	const dependencies: Map<Component["id"], Set<Component["id"]>> = new Map();

	nodes.value.forEach((node) => {
		node.outs?.forEach((outNode) => {
			if (!dependencies.has(outNode.toNodeId)) {
				dependencies.set(outNode.toNodeId, new Set());
			}
			dependencies.get(outNode.toNodeId).add(node.id);
		});
	});

	nodes.value
		.filter((node) => !dependencies.has(node.id))
		.forEach((startNode) => {
			scan(startNode, 0);
		});

	return columns;
}

function calculateAutoArrangeDimensions(columns: Map<number, Set<Component>>) {
	const columnDimensions: Map<number, { height: number; width: number }> =
		new Map();
	const nodeDimensions: Map<Component["id"], { height: number }> = new Map();
	columns.forEach((nodes, layer) => {
		let height = 0;
		let width = 0;
		nodes.forEach((node) => {
			const nodeEl = nodeContainerEl.value.querySelector(
				`[data-writer-id="${node.id}"]`,
			);
			if (!nodeEl) return;
			const nodeBCR = nodeEl.getBoundingClientRect();
			nodeDimensions.set(node.id, {
				height: nodeBCR.height * (1 / zoomLevel.value),
			});
			height +=
				nodeBCR.height * (1 / zoomLevel.value) + AUTOARRANGE_ROW_GAP_PX;
			width = Math.max(width, nodeBCR.width * (1 / zoomLevel.value));
		});
		columnDimensions.set(layer, {
			height: height - AUTOARRANGE_ROW_GAP_PX,
			width,
		});
	});
	return { columnDimensions, nodeDimensions };
}

function handleAutoArrange() {
	const columns = organizeNodesInColumns();
	const { columnDimensions, nodeDimensions } =
		calculateAutoArrangeDimensions(columns);
	const maxColumnHeight = Math.max(
		...Array.from(columnDimensions.values()).map(
			(dimensions) => dimensions.height,
		),
	);

	const coordinates = {};
	let x = AUTOARRANGE_COLUMN_GAP_PX;
	for (let i = 0; i < columns.size; i++) {
		const nodes = Array.from(columns.get(i)).sort((a, b) =>
			a.y > b.y ? 1 : -1,
		);
		const { width, height } = columnDimensions.get(i);
		let y = (maxColumnHeight - height) / 2 + AUTOARRANGE_ROW_GAP_PX;
		nodes.forEach((node) => {
			coordinates[node.id] = { x, y };
			y += nodeDimensions.get(node.id).height + AUTOARRANGE_ROW_GAP_PX;
		});
		x += width + AUTOARRANGE_COLUMN_GAP_PX;
	}
	changeCoordinatesMultiple(coordinates);
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
				handler: `$runWorkflowById_${workflowComponentId}`,
			},
		}),
		null,
		false,
	);
}

function handleNodeMousedown(ev: MouseEvent, nodeId: Component["id"]) {
	clearActiveOperations();
	const nodeEl = document.querySelector(`[data-writer-id="${nodeId}"]`);
	const nodeBCR = nodeEl.getBoundingClientRect();

	const x = (ev.pageX - nodeBCR.x) * (1 / zoomLevel.value);
	const y = (ev.pageY - nodeBCR.y) * (1 / zoomLevel.value);

	activeNodeMove.value = {
		nodeId,
		offset: { x, y },
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

function handleDragover(ev: DragEvent) {
	ev.preventDefault();
	ev.stopPropagation();
}

function getAdjustedCoordinates(ev: MouseEvent) {
	const canvasBCR = rootEl.value.getBoundingClientRect();
	const x =
		renderOffset.value.x + (ev.pageX - canvasBCR.x) * (1 / zoomLevel.value);
	const y =
		renderOffset.value.y + (ev.pageY - canvasBCR.y) * (1 / zoomLevel.value);
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

async function handleArrowDeleteClick(arrow: WorkflowArrowData) {
	if (!arrow.toNodeId) return;
	const out = {
		outId: arrow.fromOutId,
		toNodeId: arrow.toNodeId,
	};
	removeOut(arrow.fromNodeId, out);
}

function calculateArrow(
	fromNodeId: Component["id"],
	fromOutId: string,
	toCoordinates?: { x: number; y: number },
	toNodeId?: Component["id"],
): WorkflowArrowData {
	let x1: number, y1: number, x2: number, y2: number;
	const canvasBCR = rootEl.value?.getBoundingClientRect();
	if (!canvasBCR) {
		return;
	}
	x2 = (toCoordinates?.x - canvasBCR.x) * (1 / zoomLevel.value);
	y2 = (toCoordinates?.y - canvasBCR.y) * (1 / zoomLevel.value);
	const fromEl = document.querySelector(
		`[data-writer-id="${fromNodeId}"] [data-writer-socket-id="${fromOutId}"]`,
	);
	if (!fromEl) return;
	const fromBCR = fromEl.getBoundingClientRect();
	x1 = (fromBCR.x - canvasBCR.x + fromBCR.width / 2) * (1 / zoomLevel.value);
	y1 = (fromBCR.y - canvasBCR.y + fromBCR.height / 2) * (1 / zoomLevel.value);
	if (!fromEl) return;
	if (typeof toNodeId !== "undefined") {
		const toEl = document.querySelector(`[data-writer-id="${toNodeId}"]`);
		const toBCR = toEl.getBoundingClientRect();
		x2 = (toBCR.x - canvasBCR.x) * (1 / zoomLevel.value);
		y2 = (toBCR.y - canvasBCR.y + toBCR.height / 2) * (1 / zoomLevel.value);
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

function saveNodeMove() {
	changeCoordinatesMultiple(temporaryNodeCoordinates.value);
	temporaryNodeCoordinates.value = {};
}

function moveNode(ev: MouseEvent) {
	const { nodeId, offset } = activeNodeMove.value;
	activeNodeMove.value.isPerfected = true;
	const { x, y } = getAdjustedCoordinates(ev);

	const newX = Math.floor(x - offset.x);
	const newY = Math.floor(y - offset.y);

	const component = wf.getComponentById(nodeId);

	const translationX = newX - component.x;
	const translationY = newY - component.y;

	const isMovingNodeSelected = wfbm.selection.value.some(
		(c) => c.componentId === nodeId,
	);

	if (!isMovingNodeSelected) {
		// if the user moves a node that is not selected, we don't move other selected nodes
		temporaryNodeCoordinates.value = {
			...temporaryNodeCoordinates.value,
			[nodeId]: { x: newX, y: newY },
		};
		return;
	}

	// apply the same vector to other selected components
	const otherSelectedComponents = wfbm.selection.value
		.map((c) => wf.getComponentById(c.componentId))
		.filter(
			(c) => c.id !== nodeId && c.x !== undefined && c.y !== undefined,
		)
		.reduce<Record<string, { x: number; y: number }>>((acc, component) => {
			acc[component.id] = {
				x: component.x + translationX,
				y: component.y + translationY,
			};
			return acc;
		}, {});

	temporaryNodeCoordinates.value = {
		...temporaryNodeCoordinates.value,
		...otherSelectedComponents,
		[nodeId]: { x: newX, y: newY },
	};
}

function moveCanvas(ev: MouseEvent) {
	const canvasBCR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasBCR.x;
	const y = ev.pageY - canvasBCR.y;
	const { x: prevX, y: prevY } = activeCanvasMove.value.offset;
	activeCanvasMove.value.isPerfected = true;

	activeCanvasMove.value.offset = { x, y };
	changeRenderOffset(
		renderOffset.value.x + (prevX - x) * 1 * (1 / zoomLevel.value),
		renderOffset.value.y + (prevY - y) * 1 * (1 / zoomLevel.value),
	);
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

	const canvasBCR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasBCR.x;
	const y = ev.pageY - canvasBCR.y;

	activeCanvasMove.value = {
		offset: { x, y },
		isPerfected: false,
	};
}

async function handleMouseup(ev: MouseEvent) {
	if (activeNodeMove.value) {
		saveNodeMove();
	}
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

function createNode(type: string, x: number, y: number) {
	createAndInsertComponent(type, workflowComponentId, undefined, {
		x: Math.floor(x),
		y: Math.floor(y),
	});
}

function findAndCenterBlock(componentId: Component["id"]) {
	const el = rootEl.value.querySelector(`[data-writer-id="${componentId}"]`);
	const canvasBCR = rootEl.value?.getBoundingClientRect();
	if (!el || !canvasBCR) return;
	const { width, height } = el.getBoundingClientRect();
	const component = wf.getComponentById(componentId);
	if (!component) return;

	changeRenderOffset(
		component.x - canvasBCR.width / 2 + width / 2,
		component.y - canvasBCR.height / 2 + height / 2,
	);
}

async function handleChangeRenderOffset(payload: { x: number; y: number }) {
	await changeRenderOffset(payload.x, payload.y);
}

function setZoomLevel(level: number) {
	zoomLevel.value = Math.max(
		Math.min(ZOOM_SETTINGS.maxLevel, level),
		ZOOM_SETTINGS.minLevel,
	);
}

function handleChangeZoomLevel(payload: number) {
	setZoomLevel(payload);
}

function changeRenderOffset(x: number, y: number) {
	renderOffset.value = {
		x: Math.max(0, x),
		y: Math.max(0, y),
	};
}

function handleWheelScroll(ev: WheelEvent) {
	changeRenderOffset(
		renderOffset.value.x + ev.deltaX * (1 / zoomLevel.value),
		renderOffset.value.y + ev.deltaY * (1 / zoomLevel.value),
	);
}

function handleWheelZoom(ev: WheelEvent) {
	const WHEEL_ATENUATOR = 1 / 150; // Determines sensitivity of zoom
	const canvasBCR = rootEl.value.getBoundingClientRect();
	const preZoom = zoomLevel.value;

	// Calculate new zoom level

	zoomLevel.value = Math.min(
		Math.max(
			zoomLevel.value - ev.deltaY * WHEEL_ATENUATOR,
			ZOOM_SETTINGS.minLevel,
		),
		ZOOM_SETTINGS.maxLevel,
	);

	// Calculate how big the change was in terms of displayed surface

	const sizeDelta = {
		w:
			canvasBCR.width *
			(1 / preZoom) *
			(1 / zoomLevel.value) *
			(zoomLevel.value - preZoom),
		h:
			canvasBCR.height *
			(1 / preZoom) *
			(1 / zoomLevel.value) *
			(zoomLevel.value - preZoom),
	};

	/*
	Based on cursor position, determine where to focus the zoom action by
	distributing the space that was gained or lost.
	*/

	const correction = {
		x: (ev.pageX - canvasBCR.x) / canvasBCR.width,
		y: (ev.pageY - canvasBCR.y) / canvasBCR.height,
	};

	changeRenderOffset(
		renderOffset.value.x + sizeDelta.w * correction.x,
		renderOffset.value.y + sizeDelta.h * correction.y,
	);
}

async function handleWheel(ev: WheelEvent) {
	ev.preventDefault();

	if (!ev.ctrlKey && !isModifierKeyActive(ev)) {
		handleWheelScroll(ev);
		return;
	}
	handleWheelZoom(ev);
}

async function resetZoom() {
	const GAP_PX = 48;
	const { width, height, x, y } = rootEl.value.getBoundingClientRect();
	const nodes = nodeContainerEl.value.querySelectorAll("[data-writer-id]");
	const { maxX, maxY } = Array.from(nodes).reduce(
		(acc, node) => {
			const rect = node.getBoundingClientRect();
			return {
				maxY: Math.max(
					acc.maxY,
					(rect.bottom - y) * (1 / zoomLevel.value) +
						renderOffset.value.y,
				),
				maxX: Math.max(
					acc.maxX,
					(rect.right - x) * (1 / zoomLevel.value) +
						renderOffset.value.x,
				),
			};
		},
		{ maxY: 0, maxX: 0 },
	);

	const newZoomLevel = Math.min(
		(width - GAP_PX) / maxX,
		(height - GAP_PX) / maxY,
	);

	setZoomLevel(newZoomLevel);
	changeRenderOffset(0, 0);
}

watch(wfbm.firstSelectedItem, (newSelection) => {
	if (!newSelection) return;
	selectedArrow.value = null;
	if (!wf.isChildOf(workflowComponentId, newSelection.componentId)) return;
	if (newSelection.source !== "click") {
		findAndCenterBlock(newSelection.componentId);
	}
});

onMounted(async () => {
	await resetZoom();
	await nextTick();
	refreshArrows();
	rootEl.value?.addEventListener("wheel", handleWheel);
	arrowRefresherObserver.observe(nodeContainerEl.value, {
		attributes: true,
		attributeFilter: ["style"],
		childList: true,
		subtree: true,
		characterData: true,
	});
});

onUnmounted(() => {
	rootEl.value?.removeEventListener("wheel", handleWheel);
	arrowRefresherObserver.disconnect();
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

.workflowsToolbar {
	position: absolute;
	display: flex;
	gap: 8px;
	right: 24px;
	top: 20px;
}

.component.WorkflowsWorkflow.selected {
	background: var(--builderSubtleSeparatorColor);
}

.navigator {
	position: absolute;
	bottom: 24px;
	left: 24px;
	border-radius: 20px;
	overflow: hidden;
}

.nodeContainer {
	position: absolute;
	top: 0;
	left: 0;
	overflow: hidden;
	width: calc(100% * 1 / v-bind("zoomLevel"));
	height: calc(100% * 1 / v-bind("zoomLevel"));
	transform-origin: top left;
	transform: scale(v-bind("zoomLevel"));
}

svg {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}
</style>
