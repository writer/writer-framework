<template>
	<div
		ref="rootEl"
		class="WorkflowsWorkflow"
		@click="handleClick"
		@dragover="handleDragover"
		@drop="handleDrop"
		@drag="handleDrag"
		@dragstart="handleDragstart"
	>
		<svg width="100%" height="100%">
			<WorkflowArrow
				v-for="(arrow, arrowId) in arrows"
				:key="arrowId"
				:arrow="arrow"
				:is-selected="selectedArrow == arrowId"
				:is-engaged="
					selectedArrow == arrowId ||
					wfbm.getSelectedId() == arrow.fromNodeId ||
					wfbm.getSelectedId() == arrow.out.toNodeId
				"
				@click="handleArrowClick($event, arrowId)"
				@delete="handleDeleteClick($event, arrow)"
			></WorkflowArrow>
		</svg>
		<template v-for="component in children" :key="component.id">
			<component
				:is="renderProxiedComponent(component.id)"
				:data-writer-unselectable="isUnselectable"
				:style="{
					top: `${component.y - renderOffset.y}px`,
					left: `${component.x - renderOffset.x}px`,
				}"
				@drag="(ev: DragEvent) => handleNodeDrag(ev, component.id)"
				@dragstart="(ev: DragEvent) => handleNodeDragStart(ev)"
				@dragend="handleNodeDragend"
				@click="(ev: MouseEvent) => handleNodeClick(ev, component.id)"
				@out-select="
					(outId: string) => handleNodeOutSelect(component.id, outId)
				"
			></component>
		</template>
		<WdsButton class="runButton" variant="secondary" @click="handleRun">{{
			isRunning ? "Running..." : "Run"
		}}</WdsButton>
	</div>
</template>

<script lang="ts">
import { type Component, FieldType } from "@/writerTypes";
import WorkflowArrow from "./base/WorkflowArrow.vue";
import { watch } from "vue";
import WdsButton from "@/wds/WdsButton.vue";

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
	out: Component["outs"][number];
	isEngaged: boolean;
};
</script>
<script setup lang="ts">
import { Ref, computed, inject, nextTick, onMounted, ref } from "vue";
import { useComponentActions } from "@/builder/useComponentActions";
import { useDragDropComponent } from "@/builder/useDragDropComponent";
import injectionKeys from "@/injectionKeys";
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);

const rootEl: Ref<HTMLElement | null> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const arrows: Ref<WorkflowArrowData[]> = ref([]);
const renderOffset = ref({ x: 0, y: 0 });
const isRunning = ref(false);
let clickOffset = { x: 0, y: 0 };
const selectedArrow = ref(null);
const componentId = inject(injectionKeys.componentId);
const instancePath = inject(injectionKeys.instancePath);

const workflowComponentId = inject(injectionKeys.componentId);

const children = computed(() =>
	wf.getComponents(workflowComponentId, { sortedByPosition: true }),
);

const { createAndInsertComponent, addOut, removeOut, changeCoordinates } =
	useComponentActions(wf, wfbm);
const { getComponentInfoFromDrag } = useDragDropComponent(wf);

const activeNodeOut: Ref<{
	fromComponentId: string;
	outId: string;
} | null> = ref(null);

function refreshArrows() {
	const a = [];
	const canvasCBR = rootEl.value?.getBoundingClientRect();
	if (!canvasCBR) {
		return;
	}
	const nodes = wf.getComponents(workflowComponentId);

	nodes
		.filter((node) => node.outs?.length > 0)
		.forEach((node) => {
			const fromNodeId = node.id;
			node.outs.forEach((out) => {
				const fromEl = document.querySelector(
					`[data-writer-id="${fromNodeId}"] [data-writer-socket-id="${out.outId}"]`,
				);
				const toEl = document.querySelector(
					`[data-writer-id="${out.toNodeId}"]`,
				);
				if (!fromEl || !toEl) return;
				const fromCBR = fromEl.getBoundingClientRect();
				const toCBR = toEl.getBoundingClientRect();

				a.push({
					x1: fromCBR.x - canvasCBR.x + fromCBR.width / 2,
					y1: fromCBR.y - canvasCBR.y + fromCBR.height / 2,
					x2: toCBR.x - canvasCBR.x,
					y2: toCBR.y - canvasCBR.y + toCBR.height / 2,
					color: getComputedStyle(fromEl).backgroundColor,
					fromNodeId,
					out,
				});
			});
		});
	arrows.value = a;
}

const isUnselectable = computed(() => {
	if (activeNodeOut.value === null) return null;
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

function handleNodeOutSelect(componentId: Component["id"], outId: string) {
	activeNodeOut.value = {
		fromComponentId: componentId,
		outId,
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

function getAdjustedCoordinates(ev: DragEvent) {
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
	removeOut(arrow.fromNodeId, arrow.out);
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

function handleNodeDragend(ev: DragEvent) {
	ev.preventDefault();
}

async function handleNodeClick(ev: MouseEvent, componentId: Component["id"]) {
	if (!activeNodeOut.value) return;
	if (activeNodeOut.value.fromComponentId == componentId) return;

	addOut(activeNodeOut.value.fromComponentId, {
		toNodeId: componentId,
		outId: activeNodeOut.value.outId,
	});

	activeNodeOut.value = null;
}

async function createNode(type: string, x: number, y: number) {
	createAndInsertComponent(type, workflowComponentId, undefined, { x, y });
}

watch(
	() => wfbm.getSelectedId(),
	(newSelected) => {
		if (!newSelected) return;
		selectedArrow.value = null;
	},
);

watch(
	children,
	async (postChildren, preChildren) => {
		// Remove references when a node is deleted

		const preIds = new Set(preChildren.map((c) => c.id));
		const postIds = new Set(postChildren.map((c) => c.id));
		const removedIds = new Set(
			[...preIds].filter((cId) => !postIds.has(cId)),
		);

		if (removedIds.size > 0) {
			postChildren.forEach((c) => {
				if (!c.outs || c.outs.length === 0) return;
				c.outs = c.outs.filter((out) => !removedIds.has(out.toNodeId));
			});
			wf.sendComponentUpdate();
		}

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

.runButton {
	position: absolute;
	right: 32px;
	top: 32px;
}

.component.WorkflowsWorkflow.selected {
	background: var(--builderSubtleSeparatorColor);
}
</style>
