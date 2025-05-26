<template>
	<div class="BuilderSidebar">
		<div class="BuilderSidebar__toolbar">
			<div v-if="!isPreview" class="BuilderSidebar__toolbar__top">
				<hr />
				<BuilderSidebarButton
					icon="stacks"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="`${paneTitles.layers} (${modifierKeyName}I)`"
					:active="activePane === 'layers'"
					data-automation-action="sidebar-layers"
					@click="changeActivePane('layers')"
				/>
				<BuilderSidebarButton
					icon="dashboard_customize"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="`${paneTitles.add} (${modifierKeyName}B)`"
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
					:data-writer-tooltip="`Undo (${modifierKeyName}Z)`"
					:disabled="!undoRedoSnapshot.isUndoAvailable"
					@click="undo()"
				/>
				<BuilderSidebarButton
					data-automation-key="redo"
					data-writer-tooltip-placement="right"
					:data-writer-tooltip="`Redo (${modifierKeyName}Y)`"
					icon="redo"
					:disabled="!undoRedoSnapshot.isRedoAvailable"
					@click="redo()"
				/>
			</div>
			<div class="BuilderSidebar__toolbar__bottom">
				<hr />
				<BuilderSidebarButton
					target="_blank"
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
				<button
					type="button"
					class="BuilderSidebar__pane__header__btn"
					@click="activePane = undefined"
				>
					<span class="material-symbols-outlined">
						left_panel_close
					</span>
				</button>
			</div>
			<BuilderSidebarToolkit v-if="activePane === 'add'" />
			<BuilderSidebarComponentTree v-if="activePane === 'layers'" />
		</div>
	</div>
</template>

<script setup lang="ts">
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import BuilderSidebarButton from "./BuilderSidebarButton.vue";
import {
	computed,
	defineAsyncComponent,
	inject,
	onMounted,
	onUnmounted,
	ref,
	watch,
} from "vue";
import injectionKeys from "@/injectionKeys";
import { useLocalStorageJSON } from "@/composables/useLocalStorageJSON";
import { useComponentActions } from "../useComponentActions";
import { getModifierKeyName, isPlatformMac } from "@/core/detectPlatform";

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

const modifierKeyName = getModifierKeyName();

async function handleKeydown(ev: KeyboardEvent) {
	const isModifierKeyActive = isPlatformMac() ? ev.metaKey : ev.ctrlKey;
	if (!isModifierKeyActive) return;

	const targetEl = ev.target as HTMLElement;
	if (targetEl.closest("textarea, input, select")) return;

	switch (ev.key) {
		case "i":
			ev.preventDefault();
			activePane.value = "layers";
			break;
		case "b":
			ev.preventDefault();
			activePane.value = "add";
			break;
	}
}
const abort = new AbortController();

onMounted(() => {
	document.addEventListener("keydown", handleKeydown, {
		signal: abort.signal,
	});
});
onUnmounted(() => abort.abort());

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
	padding-top: 0px;
	padding-left: 8px;
	padding-right: 8px;
	padding-bottom: 12px;
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

.BuilderSidebar__toolbar hr {
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
.BuilderSidebar__pane__header__btn {
	background-color: transparent;
	border: none;
	cursor: pointer;
	font-size: 16px;
	display: flex;
	align-items: center;
}
</style>
