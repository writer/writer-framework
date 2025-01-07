<template>
	<TreeBranch
		ref="treeBranch"
		:component-id="componentId"
		:name="name"
		:query="query"
		:has-children="children.length > 0"
		:data-automation-key="component.type"
		:draggable="isDraggingAllowed(componentId)"
		:matched="matched"
		:selected="selected"
		@select="select"
		@dragover="handleDragOver"
		@dragstart="handleDragStart"
		@dragend="handleDragEnd"
		@drop="handleDrop"
	>
		<template #nameRight>
			<span class="BuilderSidebarComponentTreeBranch__nameRight">
				<template
					v-if="Object.keys(component.handlers ?? {}).length > 0"
				>
					<span class="middot"></span
					><i class="material-symbols-outlined">bolt</i>
				</template>
				<template v-if="!isComponentVisible(component.id)">
					<span class="middot"></span
					><i class="material-symbols-outlined">visibility_off</i>
				</template>
				<template v-if="component.isCodeManaged">
					<span class="middot"></span
					><i class="material-symbols-outlined">terminal</i>
				</template>
				<template v-if="previewText">
					<span class="middot"></span
					><span class="previewText">{{ previewText }}</span>
				</template>
			</span>
		</template>

		<template #children>
			<BuilderSidebarComponentTreeBranch
				v-for="childComponent in children"
				:key="childComponent.id"
				:component-id="childComponent.id"
				:query="query"
				@expand-branch="expand"
			/>
		</template>
	</TreeBranch>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import {
	ComponentPublicInstance,
	computed,
	inject,
	nextTick,
	ref,
	watch,
} from "vue";
import BuilderSidebarComponentTreeBranch from "./BuilderSidebarComponentTreeBranch.vue";
import { useEvaluator } from "@/renderer/useEvaluator";
import { useDragDropComponent } from "../useDragDropComponent";
import { useComponentActions } from "../useComponentActions";

import TreeBranch from "../BuilderTree.vue";

const treeBranch = ref<ComponentPublicInstance<typeof TreeBranch>>();

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const collapsed = ref(false);
const selected = computed(() => wfbm.isComponentIdSelected(props.componentId));
const {
	createAndInsertComponent,
	moveComponent,
	goToComponentParentPage,
	isDraggingAllowed,
} = useComponentActions(wf, wfbm);
const { getComponentInfoFromDrag, removeInsertionCandidacy, isParentSuitable } =
	useDragDropComponent(wf);
const { isComponentVisible } = useEvaluator(wf);
const emit = defineEmits(["expandBranch"]);

const matched = computed(() => {
	const q = props.query?.toLocaleLowerCase();
	if (!q) return true;
	if (def.value?.name.toLocaleLowerCase().includes(q)) return true;

	const matchingFields = Object.values(component.value.content).filter(
		(fieldContent) => fieldContent.toLocaleLowerCase().includes(q),
	);
	if (matchingFields.length > 0) return true;

	return false;
});

const props = defineProps<{
	componentId: Component["id"];
	query?: string;
}>();

const component = computed(() => {
	return wf.getComponentById(props.componentId);
});

const children = computed(() => {
	return wf.getComponents(props.componentId, { sortedByPosition: true });
});

const previewText = computed(() => {
	const key = def.value?.previewField;
	if (!key) return;
	const text = component.value.content?.[key];

	let shortenedText: string;
	const MAX_PREVIEW_TEXT_LENGTH = 70;
	if (text?.length > MAX_PREVIEW_TEXT_LENGTH) {
		shortenedText = text.substring(0, MAX_PREVIEW_TEXT_LENGTH) + "...";
	} else {
		shortenedText = text;
	}

	return shortenedText;
});

const def = computed(() => {
	return wf.getComponentDefinition(component.value.type);
});

const name = computed(() => {
	const type = component.value.type;
	if (type == "html" && component.value.content?.["element"]) {
		return component.value.content?.["element"];
	}
	if (type == "workflows_workflow") {
		return component.value.content?.["key"] || "Workflow";
	}
	return def.value?.name ?? `Unknown (${component.value.type})`;
});

async function select(ev: MouseEvent | KeyboardEvent) {
	goToComponentParentPage(props.componentId);
	await nextTick();
	wfbm.handleSelectionFromEvent(ev, props.componentId, undefined, "tree");
	expand();
}

function expand() {
	if (!treeBranch.value) return;
	treeBranch.value.expand();
	collapsed.value = false;
	emit("expandBranch");
}

function scrollToShow() {
	if (!treeBranch.value) return;
	const treeEl = treeBranch.value.$el.closest(".BuilderSidebarComponentTree");
	const treeBCR = treeEl.getBoundingClientRect();
	const scrollTop = treeBranch.value.$el.offsetTop - treeBCR.height / 2;
	treeEl.scrollTo({ top: scrollTop, left: 0, behavior: "smooth" });
}

function handleDragStart(ev: DragEvent) {
	wfbm.setSelection(null);
	ev.dataTransfer.setData(
		`application/json;writer=${component.value.type},${component.value.id}`,
		"{}",
	);
}

function handleDragEnd(ev: DragEvent) {
	removeInsertionCandidacy(ev);
}

function handleDragOver(ev: DragEvent) {
	const dragInfo = getComponentInfoFromDrag(ev);
	if (!dragInfo) return;
	const { draggedType, draggedId } = dragInfo;
	if (!isParentSuitable(props.componentId, draggedId, draggedType)) return;
	ev.preventDefault();
}

function handleDrop(ev: DragEvent) {
	const dragInfo = getComponentInfoFromDrag(ev);
	if (!dragInfo) return;
	const { draggedType, draggedId } = dragInfo;

	if (!draggedId) {
		createAndInsertComponent(draggedType, component.value.id);
	} else {
		moveComponent(draggedId, component.value.id);
	}

	removeInsertionCandidacy(ev);
}

watch(
	wfbm.firstSelectedItem,
	async (newSelection) => {
		if (!newSelection) return;
		if (newSelection.componentId !== props.componentId) return;
		if (newSelection.source == "tree") return;
		expand();
		await nextTick();
		scrollToShow();
	},
	{ immediate: true },
);
</script>

<style scoped>
.BuilderSidebarComponentTreeBranch {
	min-width: 170px;
}
.BuilderSidebarComponentTreeBranch__nameRight {
	display: flex;
	align-items: center;
	gap: 4px;

	flex-wrap: nowrap;
	text-wrap: nowrap;
	text-overflow: ellipsis;
	min-width: 0;
}

.previewText {
	flex-wrap: nowrap;
	text-wrap: nowrap;
	flex-grow: 1;
	white-space: nowrap;
	text-overflow: ellipsis;
	overflow: hidden;
}

.middot {
	display: inline-block;
	border-radius: 3px;
	width: 3px;
	min-width: 3px;
	height: 3px;
	background: var(--builderSecondaryTextColor);
	opacity: 0.5;
}
</style>
