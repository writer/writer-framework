<template>
	<div class="BuilderSidebar">
		<div class="BuilderSidebar__toolbar">
			<div v-if="!isPreview" class="BuilderSidebar__toolbar__top">
				<BuilderSidebarButton
					icon="stacks"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="paneTitles.layers"
					:active="activePane === 'layers'"
					data-automation-action="sidebar-layers"
					@click="changeActivePane('layers')"
				/>
				<BuilderSidebarButton
					icon="dashboard_customize"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="paneTitles.add"
					:active="activePane === 'add'"
					data-automation-action="sidebar-add"
					@click="changeActivePane('add')"
				/>
			</div>
			<div v-if="!isPreview" class="BuilderSidebar__toolbar__center">
				<hr />
				<BuilderSidebarButton
					icon="undo"
					data-automation-key="undo"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="
						undoRedoSnapshot.isUndoAvailable
							? `Undo: ${undoRedoSnapshot.undoDesc}`
							: 'Nothing to undo'
					"
					:disabled="!undoRedoSnapshot.isUndoAvailable"
					@click="undo()"
				/>
				<BuilderSidebarButton
					data-automation-key="redo"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="
						undoRedoSnapshot.isRedoAvailable
							? `Redo: ${undoRedoSnapshot.redoDesc}`
							: 'Nothing to redo'
					"
					icon="redo"
					:disabled="!undoRedoSnapshot.isRedoAvailable"
					@click="redo()"
				/>
			</div>
			<div class="BuilderSidebar__toolbar__bottom">
				<BuilderSidebarButton
					href="https://dev.writer.com/framework/"
					icon="help"
					data-writer-tooltip-placement="right"
					data-writer-tooltip="Docs"
				/>
			</div>
		</div>
		<div v-if="activePane && !isPreview" class="BuilderSidebar__pane">
			<div class="BuilderSidebar__pane__header">
				<h2>{{ paneTitles[activePane] }}</h2>
				<WdsButton
					variant="neutral"
					size="smallIcon"
					@click="activePane = undefined"
				>
					<span class="material-symbols-outlined">
						left_panel_close
					</span>
				</WdsButton>
			</div>
			<BuilderSidebarToolkit v-if="activePane === 'add'" />
			<BuilderSidebarComponentTree v-if="activePane === 'layers'" />
		</div>
	</div>
</template>

<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import BuilderSidebarButton from "./BuilderSidebarButton.vue";
import { computed, defineAsyncComponent, inject, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import { useLocalStorageJSON } from "@/composables/useLocalStorageJSON";
import { useComponentActions } from "../useComponentActions";

const BuilderSidebarToolkit = defineAsyncComponent({
	loader: () => import("./BuilderSidebarToolkit.vue"),
	loadingComponent: BuilderAsyncLoader,
});
const BuilderSidebarComponentTree = defineAsyncComponent({
	loader: () => import("./BuilderSidebarComponentTree.vue"),
	loadingComponent: BuilderAsyncLoader,
});

type Pane = "layers" | "add";

function isPane(v: unknown): v is Pane {
	return typeof v === "string" && ["layers", "add"].includes(v);
}

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const undoRedoSnapshot = computed(() => getUndoRedoSnapshot());
const { undo, redo, getUndoRedoSnapshot } = useComponentActions(wf, wfbm);

const isPreview = computed(() => wfbm.mode.value === "preview");

const activePaneLocalStorage = useLocalStorageJSON<Pane>("activePane", isPane);

const activePane = ref<Pane>(
	isPreview.value ? undefined : activePaneLocalStorage.value,
);

watch(activePane, () => (activePaneLocalStorage.value = activePane.value));
watch(isPreview, () => {
	if (isPreview.value) activePane.value === undefined;
});

const paneTitles = computed<Record<Pane, string>>(() => ({
	layers: wfbm.mode.value === "ui" ? "Interface Layers" : "Blueprint Layers",
	add: "Add block",
}));

function changeActivePane(value: Pane) {
	activePane.value = activePane.value === value ? undefined : value;
}
</script>

<style scoped>
.BuilderSidebar {
	display: grid;
	grid-template-columns: 48px;
	grid-template-rows: 100%;
}
.BuilderSidebar:has(.BuilderSidebar__pane) {
	grid-template-columns: 48px 240px;
}

.BuilderSidebar__toolbar {
	padding: 12px 8px;
	background: var(--wdsColorBlack);
	display: grid;
	grid-template-rows: auto 1fr auto;
	gap: 12px;
}

.BuilderSidebar__toolbar__top,
.BuilderSidebar__toolbar__center,
.BuilderSidebar__toolbar__bottom {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: flex-start;
	gap: 12px;
}

.BuilderSidebar__toolbar__top {
	grid-row: 1 / 1;
}
.BuilderSidebar__toolbar__center {
	grid-row: 2 / 2;
}
.BuilderSidebar__toolbar__bottom {
	grid-row: 3 / 3;
}

.BuilderSidebar__toolbar__center hr {
	border: none;
	border-top: 1px solid var(--wdsColorGray6);
	width: 100%;
}

.BuilderSidebar__pane {
	height: 100%;
	display: grid;
	grid-template-rows: auto 1fr;
}
.BuilderSidebar__pane__header {
	padding: 16px 16px 0 16px;
	display: grid;
	grid-template-columns: 1fr auto;
	align-items: center;
}
.BuilderSidebar__pane__header h2 {
	color: var(--wdsColorGray6);
	font-weight: 500;
	font-size: 16px;
}
</style>
