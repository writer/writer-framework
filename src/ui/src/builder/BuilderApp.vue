<template>
	<div class="BuilderApp" tabindex="-1" :style="WDS_CSS_PROPERTIES">
		<div
			class="mainGrid"
			:class="{ openPanels: ssbm.openPanels.value.size > 0 }"
		>
			<BuilderHeader class="builderHeader" />
			<BuilderSidebar
				v-show="builderMode === 'ui' || builderMode === 'blueprints'"
				class="sidebar"
				@active-pane-changed="refreshNotesPosition"
			/>
			<div class="builderMain">
				<BuilderVault v-if="builderMode === 'vault'" />
				<div
					v-else
					class="rendererWrapper"
					:class="{
						addNoteCursor:
							notesManager.isAnnotating.value &&
							ssbm.mode.value !== 'preview',
					}"
					@scroll="refreshNotesPosition"
				>
					<ComponentRenderer
						class="componentRenderer"
						:class="{
							settingsOpen: ssbm.isSingleSelectionActive,
						}"
						@dragover="handleRendererDragover"
						@dragstart="handleRendererDragStart"
						@dragend="handleRendererDragEnd"
						@drop="handleRendererDrop"
						@click.capture="handleRendererClick"
						@dblclick="handleRendererDblClick"
					>
					</ComponentRenderer>
				</div>

				<BuilderSettings
					v-if="ssbm.isSingleSelectionActive"
					:key="selectedId ?? 'noneSelected'"
				/>
			</div>
			<BuilderPanelSwitcher class="panelSwitcher" />
		</div>

		<!-- INSTANCE TRACKERS -->

		<template v-if="builderMode !== 'preview'">
			<BuilderCollaborationTracker
				class="collaborationTracker"
			></BuilderCollaborationTracker>
			<template v-if="candidateId && !isCandidacyConfirmed">
				<BuilderInstanceTracker
					:key="candidateInstancePath"
					class="insertionOverlayTracker"
					:is-off-bounds-allowed="true"
					:instance-path="candidateInstancePath"
					:match-size="true"
				>
					<BuilderInsertionOverlay />
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

		<!-- NOTES -->

		<template v-if="builderMode === 'ui'">
			<BuilderInstanceTracker
				v-for="note of notes"
				:key="note.id"
				ref="noteEl"
				class="BuilderApp__noteTracker"
				:is-off-bounds-allowed="true"
				:instance-path="note.parentInstancePath"
				:match-size="true"
			>
				<BaseNote
					class="BuilderApp__noteTracker__note"
					:component-id="note.id"
				/>
			</BuilderInstanceTracker>
		</template>

		<!-- MODAL -->

		<div id="modal"></div>

		<!-- TOOLTIP -->

		<BuilderTooltip id="tooltip" />
		<BuilderToasts />
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	defineAsyncComponent,
	inject,
	onMounted,
	onUnmounted,
	watch,
	useTemplateRef,
} from "vue";
import { useDragDropComponent } from "./useDragDropComponent";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "@/injectionKeys";
import { isPlatformMac } from "@/core/detectPlatform";
import BuilderHeader from "./BuilderHeader.vue";
import BuilderTooltip from "./BuilderTooltip.vue";
import BuilderAsyncLoader from "./BuilderAsyncLoader.vue";
import BuilderPanelSwitcher from "./panels/BuilderPanelSwitcher.vue";
import BuilderSidebar from "./sidebar/BuilderSidebar.vue";
import { WDS_CSS_PROPERTIES } from "@/wds/tokens";
import { SelectionStatus } from "./builderManager";
import BuilderToasts from "./BuilderToasts.vue";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { useToasts } from "./useToast";
import BuilderInstanceTracker from "./BuilderInstanceTracker.vue";
import BuilderCollaborationTracker from "./BuilderCollaborationTracker.vue";
import BaseNote from "@/components/core/base/BaseNote.vue";

const BuilderSettings = defineAsyncComponent({
	loader: () => import("./settings/BuilderSettings.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const ComponentRenderer = defineAsyncComponent({
	loader: () => import("@/renderer/ComponentRenderer.vue"),
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
const BuilderVault = defineAsyncComponent({
	loader: () => import("./BuilderVault.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const notesManager = inject(injectionKeys.notesManager);
const collaborationManager = inject(injectionKeys.collaborationManager);

const tracking = useWriterTracking(wf);
const toasts = useToasts();

const noteEl = useTemplateRef("noteEl");

function refreshNotesPosition() {
	const isNotesIterable =
		noteEl.value != null &&
		typeof noteEl.value[Symbol.iterator] === "function";
	if (!isNotesIterable) return;

	for (const el of noteEl.value) el.refresh();
}

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
	isGoToChildAllowed,
	isGoToNextSiblingAllowed,
	isGoToPrevSiblingAllowed,
	pasteComponent,
	copyComponent,
	removeComponentsSubtree,
	goToParent,
	goToChild,
	goToNextSibling,
	goToPrevSibling,
	moveComponentToParent,
	moveComponentInsideNextSibling,
} = useComponentActions(wf, ssbm, tracking);

const builderMode = ssbm.mode;
const selectedId = ssbm.firstSelectedId;

const notes = computed(() =>
	Array.from(notesManager.getNotes(wf.activePageId.value))
		.map((n) => ({
			...n,
			parentInstancePath:
				notesManager.useNoteInformation(n).parentInstancePath.value,
		}))
		.filter((n) => n.parentInstancePath !== undefined),
);

async function handleKeydown(ev: KeyboardEvent) {
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

	if (!ssbm.isSingleSelectionActive.value || !ssbm.firstSelectedItem.value) {
		return;
	}

	const { componentId: selectedId, instancePath: selectedInstancePath } =
		ssbm.firstSelectedItem.value;

	if (ev.key == "Delete") {
		const componentIds = ssbm.selection.value
			.filter((s) => isDeleteAllowed(s.componentId))
			.map((s) => s.componentId);
		removeComponentsSubtree(...componentIds);
		return;
	}
	if (!isModifierKeyActive) return;

	if (ev.shiftKey) {
		switch (ev.key) {
			case "ArrowDown":
				ev.preventDefault();
				if (isGoToNextSiblingAllowed(selectedId))
					goToNextSibling(selectedId);
				break;
			case "ArrowUp":
				ev.preventDefault();
				if (isGoToPrevSiblingAllowed(selectedId))
					goToPrevSibling(selectedId);
				break;
			case "ArrowLeft":
				ev.preventDefault();
				if (isGoToParentAllowed(selectedId))
					goToParent(selectedId, selectedInstancePath);
				break;
			case "ArrowRight":
				ev.preventDefault();
				if (isGoToChildAllowed(selectedId)) goToChild(selectedId);
				break;
		}
	} else {
		switch (ev.key) {
			case "ArrowDown":
				ev.preventDefault();
				moveComponentDown(selectedId);
				break;
			case "ArrowUp":
				ev.preventDefault();
				moveComponentUp(selectedId);
				break;
			case "ArrowLeft":
				ev.preventDefault();
				moveComponentToParent(selectedId);
				break;
			case "ArrowRight":
				ev.preventDefault();
				moveComponentInsideNextSibling(selectedId);
				break;
			case "v":
				if (!isPasteAllowed(selectedId)) return;
				try {
					await pasteComponent(selectedId);
				} catch (error) {
					toasts.pushToast({ type: "error", message: String(error) });
				}
				break;
			case "c":
				if (isCopyAllowed(selectedId)) copyComponent(selectedId);
				break;
			case "x":
				if (isCutAllowed(selectedId)) cutComponent(selectedId);
				break;
		}
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

	const isAlreadySelected = ssbm.isComponentIdSelected(targetId);

	if (
		isAlreadySelected &&
		ssbm.selectionStatus.value !== SelectionStatus.Multiple
	) {
		return;
	}

	if (notesManager.isAnnotating.value) return;

	ev.preventDefault();
	ev.stopPropagation();

	ssbm.handleSelectionFromEvent(ev, targetId, targetInstancePath, "click");
}
function handleRendererDblClick() {
	ssbm.isSettingsBarCollapsed.value = false;
}

const handleRendererDragStart = (ev: DragEvent) => {
	if (builderMode.value === "preview") return;

	const targetEl: HTMLElement = (ev.target as HTMLElement).closest(
		"[data-writer-id]",
	);

	const componentId = targetEl.dataset.writerId;
	const { type } = wf.getComponentById(componentId);

	// we don't support yet dragginfg multiple components in UI. If drag is starting with multiple selections, we select only one component
	if (ssbm.selectionStatus.value === SelectionStatus.Multiple) {
		ssbm.setSelection(componentId, undefined, "click");
		ssbm.isSettingsBarCollapsed.value = true;
	}

	ev.dataTransfer.setData(
		`application/json;writer=${type},${componentId}`,
		"{}",
	);
};

function handleRendererDragEnd(ev: DragEvent) {
	ssbm.setSelection(null);
	removeInsertionCandidacy(ev);
}

const abort = new AbortController();

watch(ssbm.selection, () => {
	if (!collaborationManager) return;
	collaborationManager.updateOutgoingPing({
		action: "select",
		selection: ssbm.selection.value,
	});
	collaborationManager.sendCollaborationPing();
});

onMounted(() => {
	document.addEventListener("keydown", handleKeydown, {
		signal: abort.signal,
	});
});

onUnmounted(() => {
	abort.abort();
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

.BuilderApp__noteTracker__note {
	margin-top: -30px;
	padding: 0;
	pointer-events: auto;
}

.mainGrid {
	width: 100vw;
	height: 100vh;
	grid-template-columns: auto 1fr;
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
.rendererWrapper--annotating {
	cursor: context-menu;
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

.collaborationTracker,
.insertionLabelTracker {
	z-index: 3;
	isolation: isolate;
}

.insertionOverlayTracker {
	z-index: 1;
	isolation: isolate;
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
