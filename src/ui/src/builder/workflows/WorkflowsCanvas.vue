<template>
	<div
		ref="rootEl"
		class="WorkflowsCanvas"
		@dragover="handleCanvasDragover"
		@drop="handleCanvasDrop"
	>
		<svg width="100%" height="100%">
			<WorkflowsArrow
				v-for="(arrow, arrowId) in arrows"
				:key="arrowId"
				:arrow="arrow"
				@click="handleArrowClick"
			></WorkflowsArrow>
		</svg>
		<WorkflowsNodeBox
			v-for="(node, nodeId) in nodes"
			:key="nodeId"
			:data-writer-id="nodeId"
			:node="node"
			draggable="true"
			@click="() => handleNodeClick(nodeId)"
			@drag="handleNodeDrag"
			@dragstart="handleNodeDragStart"
			@out-select="(outId) => handleNodeOutSelect(nodeId, outId)"
		></WorkflowsNodeBox>
	</div>
</template>

<script setup lang="ts">
import WorkflowsNodeBox from "./WorkflowsNodeBox.vue";
import WorkflowsArrow from "./WorkflowsArrow.vue";
import { Ref, computed, ref } from "vue";
import { onMounted } from "vue";
import { type WorkflowsComponent } from "../../writerTypes";

const rootEl: Ref<HTMLElement> = ref(null);

let activeNodeOut: { outId: string; fromNodeId: string } | null = null;

const nodes: Ref<Record<string, WorkflowsComponent>> = ref({});

let arrows = ref([]);

let nodeClickOffset = { x: 0, y: 0 };

function handleCanvasDragover(ev: DragEvent) {
	ev.preventDefault();
}

function handleCanvasDrop(ev: DragEvent) {
	ev.preventDefault();
	const rawDragData = ev.dataTransfer.getData("application/json;writer=node");
	if (!rawDragData) return;
	const dragData = JSON.parse(rawDragData);
	const id = `abcd${Math.floor(Math.random() * 2000)}`;
	const canvasCBR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasCBR.x;
	const y = ev.pageY - canvasCBR.y;
	nodes.value[id] = {
		id,
		x,
		y,
		content: {},
		type: dragData.type,
		outs: [],
	};
}

function handleNodeDragStart(ev: DragEvent) {
	const el = ev.target as HTMLElement;
	const nodeId = el.dataset.writerId;
	var img = new Image();
	img.src =
		"data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=";
	ev.dataTransfer.setDragImage(img, 0, 0);
	nodeClickOffset = {
		x: ev.offsetX,
		y: ev.offsetY,
	};
}

function handleNodeDrag(ev: DragEvent) {
	const el = ev.target as HTMLElement;
	const nodeId = el.dataset.writerId;
	const canvasCBR = rootEl.value.getBoundingClientRect();
	const x = ev.pageX - canvasCBR.x - nodeClickOffset.x;
	const y = ev.pageY - canvasCBR.y - nodeClickOffset.y;
	nodes.value[nodeId].x = Math.max(0, x);
	nodes.value[nodeId].y = Math.max(0, y);
	refreshArrows();
}

function handleNodeOutSelect(nodeId, outId) {
	activeNodeOut = {
		fromNodeId: nodeId,
		outId,
	};
}

function handleNodeClick(nodeId: string) {
	if (!activeNodeOut) return;
	if (activeNodeOut.fromNodeId == nodeId) return;
	nodes.value[activeNodeOut.fromNodeId].outs.push({
		toNodeId: nodeId,
		outId: activeNodeOut.outId,
	});
	activeNodeOut = null;
	refreshArrows();
}

function handleArrowClick() {
	console.log("Arrow has been clicked");
}

function refreshArrows() {
	arrows.value = [];
	const canvasCBR = rootEl.value.getBoundingClientRect();

	Object.entries(nodes.value)
		.filter(([nodeId, node]) => node.outs?.length > 0)
		.forEach(([nodeId, node]) => {
			const fromNodeId = nodeId;
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
				arrows.value.push({
					x1: fromCBR.x - canvasCBR.x + fromCBR.width / 2,
					y1: fromCBR.y - canvasCBR.y + fromCBR.height / 2,
					x2: toCBR.x - canvasCBR.x,
					y2: toCBR.y - canvasCBR.y + toCBR.height / 2,
					color: getComputedStyle(fromEl).backgroundColor,
				});
			});
		});
}

onMounted(() => {
	refreshArrows();
});
</script>

<style scoped>
@import "../sharedStyles.css";

.WorkflowsCanvas {
	background: var(--builderBackgroundColor);
	position: relative;
	height: 100%;
	width: 100%;
	min-height: 100%;
	min-width: 100%;
	overflow: hidden;
}

svg {
	position: absolute;
	background: var(--builderSubtleSeparatorColor);
	top: 0;
	left: 0;
}
</style>
