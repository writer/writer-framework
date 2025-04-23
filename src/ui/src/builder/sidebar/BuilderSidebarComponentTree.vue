<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarComponentTree"
		placeholder="Component tree"
		:search-count="searchResultCount"
	>
		<div>
			<BuilderSidebarComponentTreeBranch
				class="rootBranch"
				:component-id="rootComponentId"
				:query="query"
			/>
		</div>

		<template #footer>
			<div class="add">
				<WdsButton
					v-if="rootComponentId == 'root'"
					variant="special"
					size="small"
					data-automation-action="add-page"
					@click="addPage"
				>
					<i class="material-symbols-outlined"> add </i> Add
					page</WdsButton
				>
				<WdsButton
					v-if="rootComponentId == 'blueprints_root'"
					variant="special"
					size="small"
					data-automation-action="add-blueprint"
					@click="addBlueprint"
				>
					<i class="material-symbols-outlined"> add </i> Add
					blueprint</WdsButton
				>
			</div>
		</template>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { inject, nextTick, ref } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import injectionKeys from "@/injectionKeys";
import BuilderSidebarComponentTreeBranch from "./BuilderSidebarComponentTreeBranch.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { useComponentActions } from "../useComponentActions";
import { useComponentsTreeSearchResults } from "./composables/useComponentsTreeSearch";
import { useSegmentTracking } from "@/composables/useSegmentTracking";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const query = ref("");

const tracking = useSegmentTracking(wf);
const { createAndInsertComponent } = useComponentActions(wf, wfbm, tracking);

const rootComponentId = wfbm.activeRootId;

const { searchResultCount } = useComponentsTreeSearchResults(
	wf,
	query,
	rootComponentId,
);

async function addPage() {
	const pageId = createAndInsertComponent("page", "root");
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
	tracking.track("ui_page_added");
}

async function addBlueprint() {
	const pageId = createAndInsertComponent(
		"blueprints_blueprint",
		"blueprints_root",
	);
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
	tracking.track("blueprints_new_added");
}
</script>

<style scoped>
.BuilderSidebarComponentTree {
	height: 100%;
	position: relative;
}

.category .header {
	font-size: 12px;
	font-weight: 500;
	line-height: 12px; /* 100% */
	letter-spacing: 1.3px;
	text-transform: uppercase;
	color: var(--builderSecondaryTextColor);
	margin-bottom: 16px;
}

.rootBranch {
	margin-top: -8px;
	flex: 1 0 auto;
}

.tools {
	display: grid;
	grid-template-columns: 24px 1fr;
	grid-template-rows: auto;
	padding: 0 8px 0 8px;
	row-gap: 12px;
	column-gap: 4px;
}

.add {
	flex: 0 0 48px;
	bottom: 0;
	height: 48px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-top: 1px solid var(--builderSeparatorColor);
	background: var(--builderBackgroundColor);
}
</style>
