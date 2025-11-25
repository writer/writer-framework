<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarComponentTree"
		placeholder="Component tree"
		:search-count="searchResultCount"
	>
		<!-- UI mode: show pages -->
		<div v-if="rootComponentId == 'root'">
			<BuilderSidebarComponentTreeBranch
				class="rootBranch"
				:component-id="rootComponentId"
				:query="query"
			/>
		</div>

		<!-- Blueprints mode: show sections -->
		<div v-else-if="rootComponentId == 'blueprints_root'" class="sections">
			<!-- Blueprints Section -->
			<div class="section">
				<div class="section__header">
					<span class="section__title">Blueprints</span>
					<WdsButton
						variant="neutral"
						size="smallIcon"
						data-automation-action="add-blueprint"
						@click="addBlueprint"
					>
						<WdsIcon name="plus" />
					</WdsButton>
				</div>
				<div class="section__content">
					<BuilderSidebarComponentTreeBranch
						v-for="blueprint in regularBlueprints"
						:key="blueprint.id"
						:component-id="blueprint.id"
						:query="query"
					/>
					<div v-if="regularBlueprints.length === 0" class="section__empty">
						No blueprints yet
					</div>
				</div>
			</div>

			<!-- Shared Blueprints Section -->
			<div
				v-if="wf.featureFlags.value?.includes('shared_blueprints')"
				class="section"
			>
				<div class="section__header">
					<span class="section__title">Shared Blueprints</span>
					<WdsButton
						variant="neutral"
						size="smallIcon"
						data-automation-action="add-shared-blueprint"
						@click="addSharedBlueprint"
					>
						<WdsIcon name="plus" />
					</WdsButton>
				</div>
				<div class="section__content">
					<BuilderSidebarComponentTreeBranch
						v-for="blueprint in sharedBlueprintItems"
						:key="blueprint.id"
						:component-id="blueprint.id"
						:query="query"
					/>
					<div
						v-if="sharedBlueprintItems.length === 0"
						class="section__empty"
					>
						No shared blueprints yet
					</div>
				</div>
			</div>
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
					<WdsIcon name="plus" />
					Add page
				</WdsButton>
				<WdsButton
					v-if="rootComponentId == 'blueprints_root'"
					variant="special"
					size="small"
					data-automation-action="add-blueprint-footer"
					@click="addBlueprint"
				>
					<WdsIcon name="plus" />
					Add blueprint
				</WdsButton>
			</div>
		</template>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { computed, inject, nextTick, ref } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import injectionKeys from "@/injectionKeys";
import BuilderSidebarComponentTreeBranch from "./BuilderSidebarComponentTreeBranch.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { useComponentActions } from "../useComponentActions";
import { useComponentsTreeSearchResults } from "./composables/useComponentsTreeSearch";
import { useWriterTracking } from "@/composables/useWriterTracking";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const query = ref("");

const tracking = useWriterTracking(wf);
const { createAndInsertComponent, setContentValue } = useComponentActions(
	wf,
	wfbm,
	tracking,
);

const rootComponentId = wfbm.activeRootId;

const { searchResultCount } = useComponentsTreeSearchResults(
	wf,
	query,
	rootComponentId,
);

// Get all blueprints from blueprints_root
const allBlueprints = computed(() => {
	return wf.getComponents("blueprints_root", { sortedByPosition: true });
});

// Split blueprints into regular and shared blueprints
const regularBlueprints = computed(() => {
	return allBlueprints.value.filter(
		(c) => !c.content?.isSharedBlueprint,
	);
});

const sharedBlueprintItems = computed(() => {
	return allBlueprints.value.filter(
		(c) => c.content?.isSharedBlueprint === true,
	);
});

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

async function addSharedBlueprint() {
	const pageId = createAndInsertComponent(
		"blueprints_blueprint",
		"blueprints_root",
	);
	// Mark as shared blueprint
	setContentValue(pageId, "isSharedBlueprint", true);
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
	tracking.track("shared_blueprint_new_added");
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
	flex: 0 0 var(--builderPanelSwitcherHeight);
	bottom: 0;
	height: var(--builderPanelSwitcherHeight);
	display: flex;
	align-items: center;
	justify-content: center;
	border-top: 1px solid var(--builderSeparatorColor);
	background: var(--builderBackgroundColor);
}

.sections {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.section {
	display: flex;
	flex-direction: column;
}

.section__header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 8px 16px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.section__title {
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	color: var(--builderSecondaryTextColor);
}

.section__content {
	padding: 8px 0;
}

.section__empty {
	padding: 8px 16px;
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
	font-style: italic;
}
</style>
