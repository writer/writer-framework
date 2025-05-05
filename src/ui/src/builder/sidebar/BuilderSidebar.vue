<template>
	<div class="BuilderSidebar">
		<div class="BuilderSidebar__toolbar">
			<template v-if="!isPreview">
				<BuilderSidebarButton
					icon="stacks"
					:active="activePane === 'layers'"
					@click="changeActivePane('layers')"
				/>
				<BuilderSidebarButton
					icon="dashboard_customize"
					:active="activePane === 'add'"
					@click="changeActivePane('add')"
				/>
			</template>
		</div>
		<div v-if="activePane && !isPreview" class="BuilderSidebar__pane">
			<div class="BuilderSidebar__pane__header">
				<h2>{{ PANE_TITLE[activePane] }}</h2>
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

const wfbm = inject(injectionKeys.builderManager);

const isPreview = computed(() => wfbm.mode.value === "preview");

const activePaneLocalStorage = useLocalStorageJSON<Pane>("activePane", isPane);

const activePane = ref<Pane>(
	isPreview.value ? undefined : activePaneLocalStorage.value,
);

watch(activePane, () => (activePaneLocalStorage.value = activePane.value));
watch(isPreview, () => {
	if (isPreview.value) activePane.value === undefined;
});

const PANE_TITLE: Record<Pane, string> = {
	layers: "Layers",
	add: "Add block",
};

function changeActivePane(value: Pane) {
	activePane.value = activePane.value === value ? undefined : value;
}

// v-if="builderMode !== 'preview'"
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
	padding-top: 12px;
	background: var(--wdsColorBlack);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: flex-start;
	gap: 12px;
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
