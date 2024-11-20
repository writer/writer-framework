<template>
	<div class="BuilderApp" tabindex="-1">
		<div class="mainGrid">
			<BuilderHeader class="builderHeader"></BuilderHeader>
			<div v-if="builderMode !== 'preview'" class="sidebar">
				<BuilderSidebar></BuilderSidebar>
			</div>
			<div class="builderMain">
				<div class="rendererWrapper">
					<ComponentRenderer
						class="componentRenderer"
						:class="{
							settingsOpen: ssbm.isSelectionActive(),
						}"
						@dragover="handleRendererDragover"
						@dragstart="handleRendererDragStart"
						@dragend="handleRendererDragEnd"
						@drop="handleRendererDrop"
						@click.capture="handleRendererClick"
					>
					</ComponentRenderer>
				</div>

				<div
					v-if="ssbm.isSelectionActive()"
					:key="selectedId ?? 'noneSelected'"
					class="settingsBar"
				>
					<div>
						<BuilderSettings></BuilderSettings>
					</div>
				</div>
			</div>
			<div class="builderPanels">
				<BuilderCodePanel
					v-if="ssbm.openPanels.has('code')"
				></BuilderCodePanel>
				<BuilderLogPanel
					v-if="ssbm.openPanels.has('log')"
				></BuilderLogPanel>
			</div>
		</div>

		<!-- INSTANCE TRACKERS -->

		<template v-if="builderMode !== 'preview'">
			<BuilderInstanceTracker
				v-if="ssbm.isSelectionActive()"
				:key="selectedInstancePath"
				class="shortcutsTracker"
				:prevent-settings-bar-overlap="true"
				:instance-path="selectedInstancePath"
				:vertical-offset-pixels="-48"
				data-writer-cage
				@dragstart="handleRendererDragStart"
				@dragend="handleRendererDragEnd"
			>
				<BuilderComponentShortcuts
					:component-id="selectedId"
					:instance-path="selectedInstancePath"
				></BuilderComponentShortcuts>
			</BuilderInstanceTracker>
			<template v-if="candidateId && !isCandidacyConfirmed">
				<BuilderInstanceTracker
					:key="candidateInstancePath"
					class="insertionOverlayTracker"
					:is-off-bounds-allowed="true"
					:instance-path="candidateInstancePath"
					:match-size="true"
				>
					<BuilderInsertionOverlay></BuilderInsertionOverlay>
				</BuilderInstanceTracker>
				<BuilderInstanceTracker
					:key="candidateInstancePath"
					class="insertionLabelTracker"
					:instance-path="candidateInstancePath"
					:vertical-offset-pixels="-48"
				>
					<BuilderInsertionLabel>
						{{
							wf.getComponentDefinition(
								wf.getComponentById(candidateId).type,
							).name
						}}
					</BuilderInsertionLabel>
				</BuilderInstanceTracker>
			</template>
		</template>
		<!-- MODAL -->

		<div id="modal"></div>

		<!-- TOOLTIP -->

		<BuilderTooltip id="tooltip"></BuilderTooltip>
	</div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, inject, onMounted } from "vue";
import { useDragDropComponent } from "./useDragDropComponent";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import { isPlatformMac } from "../core/detectPlatform";
import BuilderHeader from "./BuilderHeader.vue";
import BuilderTooltip from "./BuilderTooltip.vue";
import BuilderComponentShortcuts from "./BuilderComponentShortcuts.vue";
import BuilderAsyncLoader from "./BuilderAsyncLoader.vue";
import BuilderCodePanel from "./BuilderCodePanel.vue";
import BuilderLogPanel from "./BuilderLogPanel.vue";

const BuilderSettings = defineAsyncComponent({
	loader: () => import("./BuilderSettings.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const BuilderSidebar = defineAsyncComponent({
	loader: () => import("./BuilderSidebar.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const ComponentRenderer = defineAsyncComponent({
	loader: () => import("@/renderer/ComponentRenderer.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const BuilderInstanceTracker = defineAsyncComponent({
	loader: () => import("./BuilderInstanceTracker.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const BuilderInsertionOverlay = defineAsyncComponent({
	loader: () => import("./BuilderInsertionOverlay.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const BuilderInsertionLabel = defineAsyncComponent({
	loader: () => import("./BuilderInsertionLabel.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const {
	candidateId,
	candidateInstancePath,
	isCandidacyConfirmed,
	dropComponent,
	assignInsertionCandidacy,
	removeInsertionCandidacy,
} = useDragDropComponent(wf);
const {
	createAndInsertComponent,
	undo,
	redo,
	moveComponent,
	moveComponentUp,
	moveComponentDown,
	cutComponent,
	isPasteAllowed,
	isCopyAllowed,
	isCutAllowed,
	isDeleteAllowed,
	isGoToParentAllowed,
	pasteComponent,
	copyComponent,
	removeComponentSubtree,
	goToParent,
} = useComponentActions(wf, ssbm);

const builderMode = computed(() => ssbm.getMode());

const selectedId = computed(() => ssbm.getSelection()?.componentId);
const selectedInstancePath = computed(() => ssbm.getSelection()?.instancePath);
const openPanelCount = computed<number>(() => ssbm.openPanels.size);

function handleKeydown(ev: KeyboardEvent): void {
	if (ev.key == "Escape") {
		ssbm.setSelection(null);
		return;
	}

	const isModifierKeyActive = isPlatformMac() ? ev.metaKey : ev.ctrlKey;
	const targetEl = ev.target as HTMLElement;
	if (targetEl.closest("textarea, input, select")) return;

	if (ev.key == "z" && isModifierKeyActive) {
		ev.preventDefault();
		undo();
		return;
	}
	if (ev.key == "y" && isModifierKeyActive) {
		ev.preventDefault();
		redo();
		return;
	}

	if (!ssbm.isSelectionActive()) return;
	const { componentId: selectedId, instancePath: selectedInstancePath } =
		ssbm.getSelection();

	if (ev.key == "Delete") {
		if (!isDeleteAllowed(selectedId)) return;
		removeComponentSubtree(selectedId);
		return;
	}
	if (ev.key == "ArrowUp" && isModifierKeyActive && ev.shiftKey) {
		if (!isGoToParentAllowed(selectedId)) return;
		goToParent(selectedId, selectedInstancePath);
		return;
	}
	if (ev.key == "ArrowUp" && isModifierKeyActive) {
		moveComponentUp(selectedId);
		return;
	}
	if (ev.key == "ArrowDown" && isModifierKeyActive) {
		moveComponentDown(selectedId);
		return;
	}
	if (ev.key == "v" && isModifierKeyActive) {
		if (!isPasteAllowed(selectedId)) return;
		pasteComponent(selectedId);
		return;
	}
	if (ev.key == "c" && isModifierKeyActive) {
		if (!isCopyAllowed(selectedId)) return;
		copyComponent(selectedId);
		return;
	}
	if (ev.key == "x" && isModifierKeyActive) {
		if (!isCutAllowed(selectedId)) return;
		cutComponent(selectedId);
		return;
	}
}

function handleRendererDragover(ev: DragEvent) {
	if (builderMode.value === "preview") return;
	assignInsertionCandidacy(ev);
}

function handleRendererDrop(ev: DragEvent) {
	if (builderMode.value === "preview") return;
	ssbm.setSelection(null);
	const dropInfo = dropComponent(ev);
	if (!dropInfo) return;
	const { draggedType, draggedId, parentId, position } = dropInfo;

	if (!draggedId) {
		createAndInsertComponent(draggedType, parentId, position);
	} else {
		moveComponent(draggedId, parentId, position);
	}
}

function handleRendererClick(ev: PointerEvent): void {
	if (builderMode.value === "preview") return;

	const unselectableEl: HTMLElement = (ev.target as HTMLElement).closest(
		"[data-writer-unselectable]",
	);
	if (unselectableEl) return;

	const targetEl: HTMLElement = (ev.target as HTMLElement).closest(
		"[data-writer-id]",
	);
	if (!targetEl) return;
	const targetId = targetEl.dataset.writerId;
	const targetInstancePath = targetEl.dataset.writerInstancePath;
	if (targetId !== ssbm.getSelectedId()) {
		ev.preventDefault();
		ev.stopPropagation();
		ssbm.setSelection(targetId, targetInstancePath, "click");
	}
}

const handleRendererDragStart = (ev: DragEvent) => {
	if (builderMode.value === "preview") return;

	const targetEl: HTMLElement = (ev.target as HTMLElement).closest(
		"[data-writer-id]",
	);

	const componentId = targetEl.dataset.writerId;
	const { type } = wf.getComponentById(componentId);

	ev.dataTransfer.setData(
		`application/json;writer=${type},${componentId}`,
		"{}",
	);
};

function handleRendererDragEnd(ev: DragEvent) {
	ssbm.setSelection(null);
	removeInsertionCandidacy(ev);
}

onMounted(() => {
	document.addEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderApp {
	--builderBackgroundColor: #ffffff;
	--builderAccentColor: #5551ff;
	--builderSuccessColor: #3be19b;
	--builderErrorColor: #ff3d00;
	--builderHeaderBackgroundColor: #333333;
	--builderHeaderBackgroundHoleColor: #000000;
	--builderPrimaryTextColor: rgba(0, 0, 0, 0.9);
	--builderSecondaryTextColor: rgba(0, 0, 0, 0.6);
	--builderAreaSeparatorColor: rgba(0, 0, 0, 0.2);
	--builderSeparatorColor: #e4e7ed;
	--builderSubtleSeparatorColor: #f5f5f9;
	--builderIntenseSeparatorColor: #d2d4d7;
	--builderSelectedColor: #e4e9ff;
	--builderMatchingColor: #f8dccc;
	--builderIntenseSelectedColor: #0094d1;
	--builderSubtleHighlightColor: rgba(0, 0, 0, 0.05);
	--builderSubtleHighlightColorSolid: #f2f2f2;
	--builderDisabledColor: rgb(180, 180, 180);
	--builderSidebarWidth: 265px;
	--builderSettingsWidth: 450px;
	--builderActionOngoingColor: #333333;
	--builderTopBarHeight: 48px;
	--builderWarningTextColor: white;
	--builderWarningColor: #ff3d00;
	--builderPanelHeight: 50vh;

	--buttonColor: #5551ff;
	--buttonTextColor: white;
	--accentColor: var(--builderAccentColor);
	--primaryTextColor: var(--builderPrimaryTextColor);
	--separatorColor: var(--builderSeparatorColor);
	--secondaryTextColor: var(--builderSecondaryTextColor);

	font-size: 0.8rem;
	color: var(--builderPrimaryTextColor);
	font-family: "Poppins", "Helvetica Neue", "Lucida Grande", sans-serif;
	width: 100vw;
	height: 100vh;
	position: relative;
	overflow: hidden;
	background: var(--builderBackgroundColor);
}

.mainGrid {
	width: 100vw;
	height: 100vh;
	grid-template-columns:
		v-bind(
			"ssbm.getMode() !== 'preview' ? 'var(--builderSidebarWidth)' : '0px'"
		)
		1fr;
	grid-template-rows: var(--builderTopBarHeight) 1fr v-bind(
			"openPanelCount > 0 ? 'var(--builderPanelHeight)' : '0px'"
		);
	display: grid;
}

.builderHeader {
	grid-column: 1 / 3;
	grid-row: 1;
	z-index: 2;
}

.sidebar {
	grid-column: 1 / 2;
	grid-row: 2;
	min-height: 0;
	border-right: 1px solid var(--builderAreaSeparatorColor);
}

.builderMain {
	background: var(--builderBackgroundColor);
	overflow: hidden;
	position: relative;
	grid-column: 2 / 3;
	grid-row: 2;
}

.rendererWrapper {
	display: flex;
	flex-direction: column;
	height: 100%;
	overflow-y: auto;
}

.componentRenderer {
	min-height: 100%;
	flex: 1 0 auto;
}

.componentRenderer.settingsOpen {
	--notificationsDisplacement: calc(var(--builderSettingsWidth) + 24px);
}

.settingsBar {
	position: absolute;
	right: 24px;
	top: v-bind("ssbm.getMode() == 'workflows' ? '72px' : '20px'");
	z-index: 4;
	width: var(--builderSettingsWidth);
	bottom: 24px;
	overflow: hidden;
	border: 1px solid var(--builderAreaSeparatorColor);
	background: var(--builderBackgroundColor);
	box-shadow: 0px 0px 12px 4px rgba(0, 0, 0, 0.04);
	border-radius: 12px;
}

.settingsBar > div {
	overflow-y: auto;
	height: 100%;
}

.builderPanels {
	grid-column: 1 / 3;
	grid-row: 3;
	display: grid;
	grid-template-columns: repeat(v-bind("openPanelCount"), 1fr);
	grid-template-rows: 100%;
}

.builderPanels:empty {
	display: none;
}

.shortcutsTracker,
.insertionLabelTracker {
	z-index: 3;
}

.insertionOverlayTracker {
	z-index: 1;
}

#modal {
	position: absolute;
	top: 0;
	left: 0;
	z-index: 10;
}

#tooltip {
	position: absolute;
	z-index: 11;
}
</style>
