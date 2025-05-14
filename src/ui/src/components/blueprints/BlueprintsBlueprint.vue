<template>
	<div
		ref="rootEl"
		class="BlueprintsBlueprint"
		:data-writer-unselectable="isUnselectable"
		@click="handleClick"
		@dragover.prevent.stop
		@drop="handleDrop"
		@mousemove="handleMousemove"
		@mousedown="handleMousedown"
		@mouseup="handleMouseup"
	>
		<div ref="nodeContainerEl" class="nodeContainer">
			<svg>
				<defs>
					<pattern
						id="grid"
						:width="GRID_TICK"
						:height="GRID_TICK"
						patternUnits="userSpaceOnUse"
						:x="-renderOffset.x - GRID_TICK / 2"
						:y="-renderOffset.y - GRID_TICK / 2"
					>
						<circle
							:cx="GRID_TICK / 2"
							:cy="GRID_TICK / 2"
							r="1"
							:fill="WdsColor.Gray3"
						/>
					</pattern>
				</defs>

				<rect
					v-if="displayGrid"
					width="100%"
					height="100%"
					fill="url(#grid)"
					fil
				/>
				<BlueprintArrow
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
				></BlueprintArrow>
				<BlueprintArrow
					v-if="activeConnection?.liveArrow"
					key="liveArrow"
					:arrow="activeConnection.liveArrow"
					:is-selected="false"
					:is-engaged="true"
				></BlueprintArrow>
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
		<SharedCollaborationCanvas
			:render-offset="renderOffset"
			:zoom-level="zoomLevel"
		></SharedCollaborationCanvas>
		<BlueprintToolbar
			class="blueprintsToolbar"
			@autogen-click="isAutogenShown = true"
		/>
		<WdsModal v-if="isAutogenShown">
			<BlueprintsAutogen
				@block-generation="handleBlockGeneration"
			></BlueprintsAutogen>
		</WdsModal>
		<BlueprintNavigator
			v-if="nodeContainerEl"
			:node-container-el="nodeContainerEl"
			:render-offset="renderOffset"
			:zoom-level="zoomLevel"
			class="navigator"
			@auto-arrange="handleAutoArrange"
			@change-render-offset="handleChangeRenderOffset"
			@change-zoom-level="handleChangeZoomLevel"
			@reset-zoom="resetZoom"
		></BlueprintNavigator>
	</div>
</template>

<script lang="ts">
import { type Component, FieldType } from "@/writerTypes";
import BlueprintArrow from "./base/BlueprintArrow.vue";
import { watch } from "vue";
import BlueprintNavigator from "./base/BlueprintNavigator.vue";
import { isModifierKeyActive } from "@/core/detectPlatform";
import WdsModal from "@/wds/WdsModal.vue";
import BlueprintsAutogen from "./BlueprintsAutogen.vue";
import { useLogger } from "@/composables/useLogger";
import { mathCeilToMultiple } from "@/utils/math";
import { WdsColor } from "@/wds/tokens";
import { useWriterTracking } from "@/composables/useWriterTracking";
import SharedCollaborationCanvas from "../shared/SharedCollaborationCanvas.vue";

const { log } = useLogger();

const GRID_TICK = 24;

const description =
	"A container component representing a single blueprint within the application.";

export default {
	writer: {
		name: "Blueprint",
		toolkit: "blueprints",
		category: "Root",
		description,
		allowedChildrenTypes: ["*"],
		allowedParentTypes: ["blueprints_root"],
		fields: {
			key: {
				name: "Blueprint key",
				desc: "Unique identifier. It's needed to enable navigation to this Blueprint.",
				type: FieldType.IdKey,
			},
		},
	},
};

export type BlueprintArrowData = {
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
	computed,
	defineAsyncComponent,
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
import { collaborationSnapshot } from "@/composables/useCollaboration";
import injectionKeys from "@/injectionKeys";
import {
	computeDistance,
	computePointInTheGrid,
	Point,
	positionateRectangleWithoutOverlap,
	Rectangle,
	translatePoint,
} from "@/utils/geometry";

const BlueprintToolbar = defineAsyncComponent({
	loader: () => import("./base/BlueprintToolbar.vue"),
});

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);
const blueprintComponentId = inject(injectionKeys.componentId);

const rootEl = useTemplateRef("rootEl");
const nodeContainerEl = useTemplateRef("nodeContainerEl");

const arrows = shallowRef<BlueprintArrowData[]>([]);
const renderOffset = shallowRef({ x: 0, y: 0 });
const selectedArrow = shallowRef(null);
const isAutogenShown = ref(false);
const zoomLevel = ref(ZOOM_SETTINGS.initialLevel);
const arrowRefresherObserver = new MutationObserver(refreshArrows);
const temporaryNodeCoordinates = shallowRef<Record<Component["id"], Point>>({});

const emit = defineEmits(["collaborationUpdate"]);

const AUTOARRANGE_ROW_GAP_PX = GRID_TICK * 4;
const AUTOARRANGE_COLUMN_GAP_PX = GRID_TICK * 6;

const nodes = computed(() =>
	wf.getComponents(blueprintComponentId, { sortedByPosition: true }),
);

const tracking = useWriterTracking(wf);
const {
	createAndInsertComponent,
	addOut,
	removeOut,
	changeCoordinatesMultiple,
} = useComponentActions(wf, wfbm, tracking);
const { getComponentInfoFromDrag } = useDragDropComponent(wf);

const activeConnection = shallowRef<{
	fromNodeId: Component["id"];
	fromOutId: Component["outs"][number]["outId"];
	liveArrow?: BlueprintArrowData;
}>(null);

const activeNodeMove = shallowRef<{
	nodeId: Component["id"];
	offset: Point;
	isPerfected: boolean;
} | null>(null);

const activeCanvasMove = shallowRef<{
	offset: Point;
	isPerfected: boolean;
} | null>(null);

const displayGrid = useDisplayGridSetting();

function useDisplayGridSetting() {
	const key = "blueprint__hideGrid";
	const displayGrid = ref(localStorage.getItem(key) === null);
	watch(displayGrid, (v) =>
		v ? localStorage.removeItem(key) : localStorage.setItem(key, "1"),
	);
	return displayGrid;
}

function refreshArrows() {
	arrows.value = nodes.value.reduce((acc, node) => {
		if (!node.outs?.length) return acc;

		for (const out of node.outs) {
			const arrow = calculateArrow(
				node.id,
				out.outId,
				undefined,
				out.toNodeId,
			);
			if (arrow) acc.push(arrow);
		}
		return acc;
	}, []);
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
		const isFound = columns.values().find((column) => column.has(node));
		if (isFound) return;
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

function getNodeBoundingClientRect(nodeId: Component["id"]) {
	const selector = `[data-writer-id="${nodeId}"]`;
	const nodeEl = nodeContainerEl.value.querySelector(selector);
	if (!nodeEl) return;
	return nodeEl.getBoundingClientRect();
}

function getNodeRectange(nodeId: Component["id"]): Rectangle {
	const bcr = getNodeBoundingClientRect(nodeId);
	if (!bcr) return undefined;
	const canvasBCR = rootEl.value?.getBoundingClientRect();
	if (!canvasBCR) return;

	const getDimension = (v: number) => {
		const dimension = mathCeilToMultiple(v, GRID_TICK);
		// if the dimension correspond to the exact unit, we add 1 to add a gap
		return dimension === v ? dimension + 1 : dimension - 1;
	};

	return {
		x: renderOffset.value.x + (bcr.x - canvasBCR.x) * zoomRatio.value,
		y: renderOffset.value.y + (bcr.y - canvasBCR.y) * zoomRatio.value,
		width: getDimension(bcr.width * zoomRatio.value),
		height: getDimension(bcr.height * zoomRatio.value),
	};
}

function calculateAutoArrangeDimensions(columns: Map<number, Set<Component>>) {
	const columnDimensions: Map<number, { height: number; width: number }> =
		new Map();
	const nodeDimensions: Map<Component["id"], { height: number }> = new Map();
	columns.forEach((nodes, layer) => {
		let height = 0;
		let width = 0;
		nodes.forEach((node) => {
			const nodeBCR = getNodeBoundingClientRect(node.id);
			if (!nodeBCR) return;
			nodeDimensions.set(node.id, {
				height: nodeBCR.height * zoomRatio.value,
			});
			height += nodeBCR.height * zoomRatio.value + AUTOARRANGE_ROW_GAP_PX;
			width = Math.max(width, nodeBCR.width * zoomRatio.value);
		});
		columnDimensions.set(layer, {
			height: height - AUTOARRANGE_ROW_GAP_PX,
			width,
		});
	});
	return { columnDimensions, nodeDimensions };
}

function handleAutoArrange() {
	autoArrange("currentY");
}

function autoArrange(ySortStrategyKey: "currentY" | "socketPosition") {
	const ySortStrategies: Record<
		typeof ySortStrategyKey,
		(a: Component, b: Component) => number
	> = {
		currentY: (a, b) => (a.y > b.y ? 1 : -1),
		socketPosition: (a, b) => {
			const [aPre, bPre] = [a, b].map((sortComponent) =>
				nodes.value
					.map((c) =>
						c.outs
							?.filter((out) => out.toNodeId === sortComponent.id)
							.map((out) => ({
								fromNodeId: c.id,
								fromOutId: out.outId,
							})),
					)
					.filter(Boolean)
					.flat(),
			);

			if (!aPre || aPre.length === 0) return 0;
			if (!bPre || bPre.length === 0) return 0;

			const aEl = document.querySelector(
				`[data-writer-id="${aPre[0].fromNodeId}"] [data-writer-socket-id="${aPre[0].fromOutId}"]`,
			);

			const bEl = document.querySelector(
				`[data-writer-id="${bPre[0].fromNodeId}"] [data-writer-socket-id="${bPre[0].fromOutId}"]`,
			);

			if (!aEl || !bEl) return 0;

			const aElBCR = aEl.getBoundingClientRect();
			const bElBCR = bEl.getBoundingClientRect();
			return aElBCR.y > bElBCR.y ? -1 : 1;
		},
	};

	const columns = organizeNodesInColumns();
	const { columnDimensions, nodeDimensions } =
		calculateAutoArrangeDimensions(columns);
	const maxColumnHeight = Math.max(
		...Array.from(columnDimensions.values()).map(
			(dimensions) => dimensions.height,
		),
	);

	const coordinates = {};
	let x = AUTOARRANGE_COLUMN_GAP_PX / 2;
	for (let i = 0; i < columns.size; i++) {
		const nodes = Array.from(columns.get(i)).sort(
			ySortStrategies[ySortStrategyKey],
		);
		const { width, height } = columnDimensions.get(i);
		let y = mathCeilToMultiple(
			(maxColumnHeight - height) / 2 + AUTOARRANGE_ROW_GAP_PX,
			GRID_TICK,
		);
		nodes.forEach((node) => {
			const point = computePointInTheGrid({ x, y }, GRID_TICK);
			coordinates[node.id] = point;
			y += nodeDimensions.get(node.id).height + AUTOARRANGE_ROW_GAP_PX;
		});
		x += mathCeilToMultiple(width + AUTOARRANGE_COLUMN_GAP_PX, GRID_TICK);
	}
	changeCoordinatesMultiple(coordinates);
}

function handleNodeMousedown(ev: MouseEvent, nodeId: Component["id"]) {
	clearActiveOperations();
	const nodeEl = document.querySelector(`[data-writer-id="${nodeId}"]`);
	const nodeBCR = nodeEl.getBoundingClientRect();

	const x = (ev.pageX - nodeBCR.x) * zoomRatio.value;
	const y = (ev.pageY - nodeBCR.y) * zoomRatio.value;

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
	activeConnection.value = { fromNodeId, fromOutId };
}

const zoomRatio = computed(() => 1 / zoomLevel.value);
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

	createNode(draggedType, { x, y });
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

async function handleArrowDeleteClick(arrow: BlueprintArrowData) {
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
	toCoordinates?: Point,
	toNodeId?: Component["id"],
): BlueprintArrowData {
	let x1: number, y1: number, x2: number, y2: number;
	const canvasBCR = rootEl.value?.getBoundingClientRect();
	if (!canvasBCR) {
		return;
	}
	x2 = (toCoordinates?.x - canvasBCR.x) * zoomRatio.value;
	y2 = (toCoordinates?.y - canvasBCR.y) * zoomRatio.value;
	const fromEl = document.querySelector(
		`[data-writer-id="${fromNodeId}"] [data-writer-socket-id="${fromOutId}"]`,
	);
	if (!fromEl) return;
	const fromBCR = fromEl.getBoundingClientRect();
	x1 = (fromBCR.x - canvasBCR.x + fromBCR.width / 2) * zoomRatio.value;
	y1 = (fromBCR.y - canvasBCR.y + fromBCR.height / 2) * zoomRatio.value;
	if (!fromEl) return;
	if (typeof toNodeId !== "undefined") {
		const toEl = document.querySelector(`[data-writer-id="${toNodeId}"]`);
		const toBCR = toEl.getBoundingClientRect();
		x2 = (toBCR.x - canvasBCR.x) * zoomRatio.value;
		y2 = (toBCR.y - canvasBCR.y + toBCR.height / 2) * zoomRatio.value;
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
		".BlueprintsBlueprint [data-writer-id]",
	) as HTMLElement;
	return toNodeEl?.dataset.writerId;
}

function refreshLiveArrow(ev: MouseEvent) {
	let toCoordinates: Point, toNodeId: Component["id"];

	toNodeId = getHoveredNodeId(ev);
	if (typeof toNodeId == "undefined") {
		toCoordinates = { x: ev.pageX, y: ev.pageY };
	}
	const { fromNodeId, fromOutId } = activeConnection.value;
	if (toNodeId == fromNodeId) return;

	activeConnection.value = {
		...activeConnection.value,
		liveArrow: calculateArrow(
			fromNodeId,
			fromOutId,
			toCoordinates,
			toNodeId,
		),
	};
}

function clearActiveOperations() {
	activeCanvasMove.value = null;
	activeConnection.value = null;
	activeNodeMove.value = null;
}

function changeCoordinatesMultipleWithCheck(
	nodeCoordinates: Record<Component["id"], Point>,
) {
	const coordinatesFixed = Object.entries(nodeCoordinates)
		.filter(([id, point]) => {
			const c = wf.getComponentById(id);
			return c?.x !== point.x || c?.y !== point.y;
		})
		.reduce((acc, [id, point]) => {
			const newPoint = computePointInTheGrid(point, GRID_TICK);
			const currentRectangle = getNodeRectange(id);
			const rectange = { ...currentRectangle, ...newPoint };

			const otherRectangles = nodes.value
				.filter((n) => n.id !== id)
				.map((c) => getNodeRectange(c.id))
				.filter(Boolean);

			const { x, y } = positionateRectangleWithoutOverlap(
				rectange,
				otherRectangles,
				GRID_TICK,
			);
			if (currentRectangle.x !== x || currentRectangle.y !== y) {
				acc[id] = { x, y };
			}

			return acc;
		}, {});

	if (Object.keys(coordinatesFixed).length === 0) return;

	changeCoordinatesMultiple(coordinatesFixed);
}

function saveNodeMove() {
	changeCoordinatesMultipleWithCheck(temporaryNodeCoordinates.value);
	temporaryNodeCoordinates.value = {};
}

function moveNode(ev: MouseEvent) {
	const { nodeId, offset } = activeNodeMove.value;
	const { x, y } = getAdjustedCoordinates(ev);

	const newX = Math.floor(x - offset.x);
	const newY = Math.floor(y - offset.y);

	const component = wf.getComponentById(nodeId);

	const distance = computeDistance(
		{ x: component.x, y: component.y },
		{ x: newX, y: newY },
	);

	if (distance > 10) {
		// once `isPerfected` is `true`, we don't select the node. So we considerate a small movement as a missclick (the user click but drag few pixels)
		activeNodeMove.value = { ...activeNodeMove.value, isPerfected: true };
	}

	const trans = { x: newX - component.x, y: newY - component.y };

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
		.reduce<Record<string, Point>>((acc, component) => {
			acc[component.id] = translatePoint(
				{ x: component.x, y: component.y },
				trans,
			);
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

	activeCanvasMove.value = { isPerfected: true, offset: { x, y } };

	changeRenderOffset(
		renderOffset.value.x + (prevX - x) * 1 * zoomRatio.value,
		renderOffset.value.y + (prevY - y) * 1 * zoomRatio.value,
	);
}

function handleMousemove(ev: MouseEvent) {
	emit("collaborationUpdate", {
		x: ev.clientX,
		y: ev.clientY,
	});

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

function createNode(type: string, point: Point) {
	const otherRectangles = nodes.value
		.map((c) => getNodeRectange(c.id))
		.filter(Boolean);
	const { x, y } = positionateRectangleWithoutOverlap(
		{ ...point, width: 240, height: 180 },
		otherRectangles,
		GRID_TICK,
	);
	createAndInsertComponent(type, blueprintComponentId, undefined, { x, y });
}

function findAndCenterBlock(componentId: Component["id"]) {
	const componentBCR = getNodeBoundingClientRect(componentId);
	const canvasBCR = rootEl.value?.getBoundingClientRect();
	if (!componentBCR || !canvasBCR) return;
	const { width, height } = componentBCR;
	const component = wf.getComponentById(componentId);
	if (!component) return;

	changeRenderOffset(
		component.x - canvasBCR.width / 2 + width / 2,
		component.y - canvasBCR.height / 2 + height / 2,
	);
}

function handleChangeRenderOffset(payload: Point) {
	changeRenderOffset(payload.x, payload.y);
}

function handleCreateAutogenExample(description: string) {
	const simplifiedNodes = nodes.value.map((node) => {
		return {
			id: node.id,
			type: node.type,
			content: node.content,
			outs: node.outs,
		};
	});
	const stringifiedBlueprint = JSON.stringify(simplifiedNodes);
	const message = `
	<example>
		<description>
			${description}
		</description>
		<blueprint>
			${stringifiedBlueprint}
		</blueprint>
	</example>`.trim();
	log(message);
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
		renderOffset.value.x + ev.deltaX * zoomRatio.value,
		renderOffset.value.y + ev.deltaY * zoomRatio.value,
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
			zoomRatio.value *
			(zoomLevel.value - preZoom),
		h:
			canvasBCR.height *
			(1 / preZoom) *
			zoomRatio.value *
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
					(rect.bottom - y) * zoomRatio.value + renderOffset.value.y,
				),
				maxX: Math.max(
					acc.maxX,
					(rect.right - x) * zoomRatio.value + renderOffset.value.x,
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

async function handleBlockGeneration(
	payload: { components: Component[] } | null,
) {
	isAutogenShown.value = false;
	if (!payload) return;
	const { components } = payload;
	components.forEach((component) => {
		createAndInsertComponent(
			component.type,
			blueprintComponentId,
			undefined,
			component,
		);
	});

	await nextTick();
	autoArrange("socketPosition");
}

watch(wfbm.firstSelectedItem, (newSelection) => {
	if (!newSelection) return;
	selectedArrow.value = null;
	if (!wf.isChildOf(blueprintComponentId, newSelection.componentId)) return;
	if (newSelection.source !== "click") {
		findAndCenterBlock(newSelection.componentId);
	}
});

watch(collaborationSnapshot, (newSnapshot) => {
	console.log("new snapshot", newSnapshot);
});

function handleKeydown(event: KeyboardEvent) {
	const isModifiedKey = isModifierKeyActive(event);

	// toggle grid with "cmd + `" (like Figma)
	if (
		isModifiedKey &&
		(event.code === "Backquote" || event.code === "Backslash")
	) {
		displayGrid.value = !displayGrid.value;
		return;
	}

	if (!wfbm.selection.value.length) return;

	const target = event.target as HTMLElement;
	if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;

	function getDirection(): Point | undefined {
		switch (event.key) {
			case "ArrowDown":
				return { x: 0, y: GRID_TICK };
			case "ArrowUp":
				return { x: 0, y: -GRID_TICK };
			case "ArrowLeft":
				return { x: -GRID_TICK, y: 0 };
			case "ArrowRight":
				return { x: GRID_TICK, y: 0 };
		}
	}
	const direction = getDirection();
	if (direction === undefined) return;

	event.preventDefault();

	const coordinates = wfbm.selection.value
		.map((s) => wf.getComponentById(s.componentId))
		.filter((c) => c?.x !== undefined && c?.y !== undefined)
		.reduce<Record<Component["id"], Point>>((acc, c) => {
			acc[c.id] = translatePoint({ x: c.x, y: c.y }, direction);
			return acc;
		}, {});

	changeCoordinatesMultipleWithCheck(coordinates);
}

const abort = new AbortController();

onMounted(async () => {
	await resetZoom();
	await nextTick();
	refreshArrows();
	rootEl.value?.addEventListener("wheel", handleWheel, {
		signal: abort.signal,
	});

	document.addEventListener("keydown", handleKeydown, {
		signal: abort.signal,
	});
	arrowRefresherObserver.observe(nodeContainerEl.value, {
		attributes: true,
		attributeFilter: ["style"],
		childList: true,
		subtree: true,
		characterData: true,
	});

	//@ts-expect-error modifying window
	window.createAutogenExample = handleCreateAutogenExample;
});

onUnmounted(() => {
	abort.abort();
	arrowRefresherObserver.disconnect();
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.BlueprintsBlueprint {
	display: flex;
	width: 100%;
	min-height: 100%;
	background: var(--wdsColorGray0);
	flex: 1 0 auto;
	flex-direction: row;
	align-items: stretch;
	position: relative;
	overflow: hidden;
}

.blueprintsToolbar {
	position: absolute;
	display: flex;
	gap: 8px;
	right: 24px;
	top: 20px;
}

.component.BlueprintsBlueprint.selected {
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
