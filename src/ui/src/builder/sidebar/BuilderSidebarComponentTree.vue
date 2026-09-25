<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarComponentTree"
		placeholder="Component tree"
		:search-count="searchResultCount"
	>
		<div v-if="rootComponentId == 'root'">
			<BuilderSidebarComponentTreeBranch
				class="rootBranch"
				:component-id="rootComponentId"
				:query="query"
				@delete="handleComponentDelete"
			/>
		</div>

		<div v-else-if="rootComponentId == 'blueprints_root'" class="sections">
			<div
				v-for="section in blueprintSections"
				:key="section.key"
				class="section"
			>
				<div class="section__header">
					<span class="section__title">{{ section.title }}</span>
					<WdsButton
						v-if="section.showAddButton"
						variant="neutral"
						size="smallIcon"
						:data-automation-action="section.addAction"
						@click="section.onAdd"
					>
						<WdsIcon name="plus" />
					</WdsButton>
				</div>
				<div class="section__content">
					<BuilderSidebarComponentTreeBranch
						v-for="blueprint in section.items"
						:key="blueprint.id"
						:component-id="blueprint.id"
						:query="query"
						@delete="handleComponentDelete"
					/>
					<div
						v-if="section.items.length === 0"
						class="section__empty"
					>
						{{ section.emptyText }}
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
import {
	isSharedBlueprint,
	SHARED_BLUEPRINT_FLAG_VALUE,
} from "@/utils/sharedBlueprint";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const query = ref("");

const tracking = useWriterTracking(wf);
const { createAndInsertComponent, setContentValue, removeComponentSubtree } =
	useComponentActions(wf, wfbm, tracking);

const rootComponentId = wfbm.activeRootId;

const { searchResultCount } = useComponentsTreeSearchResults(
	wf,
	query,
	rootComponentId,
);

const allBlueprints = computed(() => {
	return wf.getComponents("blueprints_root", { sortedByPosition: true });
});

const regularBlueprints = computed(() => {
	return allBlueprints.value.filter((c) => !isSharedBlueprint(c));
});

const sharedBlueprintItems = computed(() => {
	return allBlueprints.value.filter((c) => isSharedBlueprint(c));
});

const isSharedBlueprintsEnabled = computed(() =>
	wf.featureFlags.value?.includes("shared_blueprints"),
);

const blueprintSections = computed(() => {
	const sections = [
		{
			key: "blueprints",
			title: "Blueprints",
			items: regularBlueprints.value,
			addAction: "add-blueprint",
			onAdd: addBlueprint,
			emptyText: "No blueprints yet",
			showAddButton: isSharedBlueprintsEnabled.value,
		},
	];

	if (isSharedBlueprintsEnabled.value) {
		sections.push({
			key: "shared-blueprints",
			title: "Shared Blueprints",
			items: sharedBlueprintItems.value,
			addAction: "add-shared-blueprint",
			onAdd: addSharedBlueprint,
			emptyText: "No shared blueprints yet",
			showAddButton: true,
		});
	}

	return sections;
});

async function addPage() {
	const pageId = createAndInsertComponent("page", "root");
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
	tracking.track("ui_page_added");
}

async function addBlueprint() {
	const key = getNewBlueprintKey();

	const pageId = createAndInsertComponent(
		"blueprints_blueprint",
		"blueprints_root",
		undefined,
		key
			? {
					content: {
						key,
					},
				}
			: undefined,
	);

	await nextTick();
	wf.setActivePageId(pageId);
	wfbm.setSelection(pageId);
	tracking.track("blueprints_new_added");
}

function getNewBlueprintKey() {
	const existingKeys = allBlueprints.value
		.map((bp) => bp.content?.key)
		.filter((key) => key?.startsWith("BLUEPRINT_"))
		.map((key) => Number.parseInt(key.replace("BLUEPRINT_", ""), 10))
		.filter((num) => !Number.isNaN(num));

	const maxIndex =
		existingKeys.length > 0
			? Math.max(...existingKeys)
			: allBlueprints.value.length + 10;
	return `BLUEPRINT_${maxIndex + 1}`;
}

async function addSharedBlueprint() {
	const pageId = createAndInsertComponent(
		"blueprints_blueprint",
		"blueprints_root",
	);
	setContentValue(pageId, "isSharedBlueprint", SHARED_BLUEPRINT_FLAG_VALUE);
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
	tracking.track("blueprints_shared_added");
}

function handleComponentDelete(componentId: string) {
	removeComponentSubtree(componentId);
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
