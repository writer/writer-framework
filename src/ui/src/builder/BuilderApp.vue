<template>
	<div class="BuilderApp" tabindex="-1" :style="WDS_CSS_PROPERTIES">
		<div
			class="mainGrid"
			:class="{ openPanels: ssbm.openPanels.value.size > 0 }"
		>
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

				<BuilderSettings
					v-if="ssbm.isSelectionActive()"
					:key="selectedId ?? 'noneSelected'"
				></BuilderSettings>
			</div>
			<BuilderPanelSwitcher class="panelSwitcher"></BuilderPanelSwitcher>
		</div>

		<!-- INSTANCE TRACKERS -->

		<template v-if="builderMode !== 'preview'">
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
import injectionKeys from "@/injectionKeys";
import { isPlatformMac } from "@/core/detectPlatform";
import BuilderHeader from "./BuilderHeader.vue";
import BuilderTooltip from "./BuilderTooltip.vue";
import BuilderAsyncLoader from "./BuilderAsyncLoader.vue";
import BuilderPanelSwitcher from "./panels/BuilderPanelSwitcher.vue";
import { WDS_CSS_PROPERTIES } from "@/wds/tokens";

const BuilderSettings = defineAsyncComponent({
	loader: () => import("./settings/BuilderSettings.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const BuilderSidebar = defineAsyncComponent({
	loader: () => import("./sidebar/BuilderSidebar.vue"),
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
	--builderBackgroundColor: var(--wdsColorWhite);
	--builderAccentColor: var(--wdsColorBlue5);
	--builderSuccessColor: var(--wdsColorGreen5);
	--builderErrorColor: var(--wdsColorOrange5);
	--builderHeaderBackgroundColor: var(--wdsColorGray6);
	--builderHeaderBackgroundHoleColor: var(--wdsColorBlack);
	--builderPrimaryTextColor: rgba(0, 0, 0, 0.9);
	--builderSecondaryTextColor: rgba(0, 0, 0, 0.6);
	--builderAreaSeparatorColor: rgba(0, 0, 0, 0.2);
	--builderSeparatorColor: var(--wdsColorGray2);
	--builderSubtleSeparatorColor: var(--wdsColorGray1);
	--builderIntenseSeparatorColor: var(--wdsColorGray3);
	--builderSelectedColor: var(--wdsColorBlue2);
	--builderMatchingColor: var(--wdsColorOrange2);
	--builderIntenseSelectedColor: var(--wdsColorBlue4);
	--builderSubtleHighlightColor: rgba(0, 0, 0, 0.05);
	--builderSubtleHighlightColorSolid: var(--wdsColorGray1);
	--builderSidebarWidth: 265px;
	--builderSettingsWidth: 450px;
	--builderActionOngoingColor: var(--wdsColorGray6);
	--builderTopBarHeight: 48px;
	--builderWarningTextColor: white;
	--builderWarningColor: var(--wdsColorOrange5);
	--builderPanelSwitcherHeight: 48px;
	--builderPanelSwitcherExpandedHeight: calc(50% - 24px);

	--buttonColor: var(--wdsColorBlue5);
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
	grid-template-rows:
		var(--builderTopBarHeight)
		1fr
		var(--builderPanelSwitcherHeight);
	display: grid;
}

.mainGrid.openPanels {
	grid-template-rows:
		var(--builderTopBarHeight)
		1fr
		var(--builderPanelSwitcherExpandedHeight);
}

.builderHeader {
	grid-column: 1 / 3;
	grid-row: 1;
	z-index: 2;
}

.sidebar {
	grid-column: 1 / 2;
	grid-row: 2 / 5;
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

.panelSwitcher {
	grid-column: 2 / 3;
	grid-row: 3;
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
