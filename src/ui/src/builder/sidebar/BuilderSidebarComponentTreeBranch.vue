<template>
	<TreeBranch
		ref="treeBranch"
		class="BuilderSidebarComponentTreeBranch"
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
import { useComponentsTreeSearchForComponent } from "./composables/useComponentsTreeSearch";
import { useComponentDescription } from "../useComponentDescription";
import { useWriterTracking } from "@/composables/useWriterTracking";

const props = defineProps({
	componentId: { type: String, required: true },
	query: { type: String, required: false, default: "" },
});

const treeBranch = ref<ComponentPublicInstance<typeof TreeBranch>>();

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const collapsed = ref(false);
const selected = computed(() => wfbm.isComponentIdSelected(props.componentId));

const tracking = useWriterTracking(wf);
const {
	createAndInsertComponent,
	moveComponent,
	goToComponentParentPage,
	isDraggingAllowed,
} = useComponentActions(wf, wfbm, tracking);
const { getComponentInfoFromDrag, removeInsertionCandidacy, isParentSuitable } =
	useDragDropComponent(wf);
const { isComponentVisible } = useEvaluator(wf);
const emit = defineEmits(["expandBranch"]);

const q = computed(() => props.query?.toLocaleLowerCase() ?? "");

const component = computed(() => wf.getComponentById(props.componentId));

const { hasMatchingChildren, matched } = useComponentsTreeSearchForComponent(
	wf,
	q,
	component,
);

watch(
	hasMatchingChildren,
	(value) => treeBranch.value?.toggleCollapse(!value),
	{
		immediate: true,
	},
);

const children = computed(() => {
	return wf.getComponents(props.componentId, { sortedByPosition: true });
});

const { name, previewText } = useComponentDescription(wf, component);

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
	const treeBranchEl = treeBranch.value?.$el as HTMLDivElement;
	if (!treeBranchEl) return;
	const treeEl = treeBranchEl.closest(".BuilderSidebarComponentTree");
	const treeBCR = treeEl.getBoundingClientRect();
	const top = treeBranch.value.$el.offsetTop - treeBCR.height / 2;
	const left = treeBranch.value.$el.offsetLeft - treeBCR.left - 16;
	treeEl.scrollTo({ top, left: Math.max(0, left), behavior: "smooth" });
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
