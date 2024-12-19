<template>
	<div ref="rootEl" class="BuilderSidebarComponentTreeBranch">
		<div
			class="main"
			:class="{ selected, notMatched, childless }"
			tabindex="0"
			:draggable="isDraggingAllowed(componentId)"
			:data-automation-key="component.type"
			@click="select"
			@keydown.enter="select"
			@dragover="handleDragOver"
			@dragstart="handleDragStart"
			@dragend="handleDragEnd"
			@drop="handleDrop"
		>
			<WdsButton
				v-if="children.length > 0"
				class="collapser"
				variant="neutral"
				size="icon"
				@click.stop="toggleCollapse"
			>
				<i v-if="collapsed" class="material-symbols-outlined"
					>expand_more</i
				>
				<i v-else class="material-symbols-outlined">expand_less</i>
			</WdsButton>

			<span class="name">{{ name }}</span>
			<template v-if="Object.keys(component.handlers ?? {}).length > 0">
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
		</div>
		<div
			v-show="(!collapsed || props.query) && children.length > 0"
			class="children"
		>
			<BuilderSidebarComponentTreeBranch
				v-for="childComponent in children"
				:key="childComponent.id"
				:component-id="childComponent.id"
				:query="query"
				@expand-branch="expand"
			></BuilderSidebarComponentTreeBranch>
		</div>
	</div>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import { computed, inject, nextTick, ref, watch } from "vue";
import BuilderSidebarComponentTreeBranch from "./BuilderSidebarComponentTreeBranch.vue";
import { useEvaluator } from "@/renderer/useEvaluator";
import { useDragDropComponent } from "../useDragDropComponent";
import { useComponentActions } from "../useComponentActions";
import WdsButton from "@/wds/WdsButton.vue";

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
const rootEl = ref<HTMLElement>(null);
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

const notMatched = computed(() => !matched.value);

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

const childless = computed(() => children.value.length == 0);

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
	if (ev.ctrlKey || ev.shiftKey) {
		wfbm.appendSelection(props.componentId, undefined, "tree");
	} else {
		wfbm.setSelection(props.componentId, undefined, "tree");
	}
	expand();
}

function expand() {
	collapsed.value = false;
	emit("expandBranch");
}

function scrollToShow() {
	if (!rootEl.value) return;
	const treeEl = rootEl.value.closest(".BuilderSidebarComponentTree");
	const treeBCR = treeEl.getBoundingClientRect();
	const scrollTop = rootEl.value.offsetTop - treeBCR.height / 2;
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

function toggleCollapse() {
	collapsed.value = !collapsed.value;
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
	font-size: 12px;
}

.main {
	padding: 8px;
	border-radius: 8px;
	cursor: pointer;
	display: flex;
	flex-wrap: nowrap;
	text-wrap: nowrap;
	max-width: 100%;
	overflow: hidden;
	align-items: center;
	outline: none;
	gap: 4px;
	color: var(--builderSecondaryTextColor);
}

.main.childless {
	padding-left: 12px;
}

.main:focus {
	outline: 1px solid var(--builderSelectedColor);
}

.main:hover {
	background: var(--builderSubtleSeparatorColor);
}

.main.selected {
	background: var(--builderSelectedColor);
}

.main.notMatched {
	filter: opacity(0.2);
}

.name {
	color: var(--builderPrimaryTextColor);
}

.previewText {
	text-wrap: nowrap;
	text-overflow: ellipsis;
	overflow: hidden;
}

.collapser {
	margin-left: -4px;
	width: 20px;
	height: 20px;
}

.middot {
	margin: 0 2px 0 2px;
	border-radius: 3px;
	width: 3px;
	min-width: 3px;
	height: 3px;
	background: var(--builderSecondaryTextColor);
	opacity: 0.5;
}

.children {
	margin-left: 20px;
}
</style>
