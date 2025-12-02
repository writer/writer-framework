<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarToolkit"
		:placeholder="placeholder"
		:search-count="searchCount"
	>
		<div v-if="isEditingSharedBlueprint" class="sharedBlueprintNotice">
			<WdsIcon name="info" />
			<span
				>Some blocks are hidden because they can't be used in shared
				blueprints.</span
			>
		</div>
		<div
			v-for="(tools, categoryId) in categories"
			:key="categoryId"
			class="category"
		>
			<div class="header">{{ categoryId }}</div>
			<div class="tools">
				<div
					v-for="tool in tools"
					:key="tool.type"
					class="tool"
					:class="{
						'tool--shared':
							categoryId === 'Shared Blueprints' &&
							isSharedBlueprintsEnabled,
					}"
					:data-writer-tooltip="tool.description"
					data-writer-tooltip-placement="right"
					data-writer-tooltip-gap="8"
					draggable="true"
					:data-component-type="tool.type"
					@dragend="handleDragEnd($event)"
					@dragstart="
						handleDragStart(
							$event,
							tool.type,
							tool.sourceBlueprintId,
						)
					"
				>
					<SharedImgWithFallback
						:alt="`(Icon for ${tool.name})`"
						draggable="false"
						:urls="getToolIcons(tool)"
						:loader-max-width-px="18"
						:loader-max-height-px="18"
					/>
					<div class="name">{{ tool.name }}</div>
					<button
						v-if="
							categoryId === 'Shared Blueprints' &&
							isSharedBlueprintsEnabled &&
							tool.sourceBlueprintId
						"
						class="tool__delete"
						:data-writer-tooltip="`Delete ${tool.name}`"
						data-writer-tooltip-placement="right"
						@click.stop="
							handleDeleteSharedBlueprint(
								tool.sourceBlueprintId,
								tool.name,
							)
						"
					>
						<WdsIcon name="trash" />
					</button>
				</div>
			</div>
		</div>

		<template v-if="rootComponentId == 'blueprints_root'" #footer>
			<div class="BuilderSidebarPanel__footer__actions">
				<WdsButton
					variant="special"
					size="small"
					class="BuilderSidebarPanel__footer__btn"
					@click="showAutogen"
				>
					<WdsIcon name="wand-sparkles" />
					Autogenerate
				</WdsButton>
			</div>
		</template>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { computed, inject, ref, watch } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import {
	getComponentDefinition,
	getSupportedComponentTypes,
} from "@/core/templateMap";
import injectionKeys from "@/injectionKeys";
import { useDragDropComponent } from "../useDragDropComponent";
import { Component } from "@/writerTypes";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { useToasts } from "../useToast";
import { useComponentActions } from "../useComponentActions";
import { useWriterTracking } from "@/composables/useWriterTracking";

const { pushToast } = useToasts();

const isAutogenModalShown = inject(
	injectionKeys.isAutogenModalShown,
	ref(false),
);
function showAutogen() {
	isAutogenModalShown.value = true;
}

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const tracking = useWriterTracking(wf);
const { removeComponentsSubtree } = useComponentActions(wf, wfbm, tracking);
const { removeInsertionCandidacy } = useDragDropComponent(wf);
const query = ref("");

const isSharedBlueprintsEnabled = computed(
	() =>
		Array.isArray(wf.featureFlags.value) &&
		wf.featureFlags.value.includes("shared_blueprints"),
);

const rootComponentId = wfbm.activeRootId;

// Get shared blueprints directly from component tree
const sharedBlueprintsFromTree = computed(() => {
	if (!isSharedBlueprintsEnabled.value) return [];
	const allBlueprints = wf.getComponents("blueprints_root", {
		sortedByPosition: true,
	});
	return allBlueprints.filter((c) => c.content?.isSharedBlueprint === true);
});

// Block types that should not be available when editing a shared blueprint
const RESTRICTED_BLOCKS_IN_SHARED_BLUEPRINT = new Set([
	"blueprints_runblueprint",
	"blueprints_apitrigger",
	"blueprints_uieventtrigger",
	"blueprints_crontrigger",
]);

// Check if we're currently editing a shared blueprint
const isEditingSharedBlueprint = computed(() => {
	if (rootComponentId.value !== "blueprints_root") return false;
	const activePageId = wf.activePageId.value;
	if (!activePageId) return false;
	const activePage = wf.getComponentById(activePageId);
	return activePage?.content?.isSharedBlueprint === true;
});

const displayedCategories = [
	"Layout",
	"Content",
	"Input",
	"Embed",
	"Writer",
	"Logic",
	"Triggers",
	"Other",
	"Shared Blueprints",
];

const activeToolkit = computed(() => {
	if (wfbm.mode.value == "blueprints") {
		return "blueprints";
	}
	return "core";
});

const categories = computed<
	Record<string, ReturnType<typeof getRelevantToolsInCategory>>
>(() => {
	const categoriesWithTools = displayedCategories
		.map((categoryId) => [
			categoryId,
			getRelevantToolsInCategory(categoryId),
		])
		.filter(
			([categoryId, tools]) =>
				tools.length > 0 ||
				(categoryId === "Shared Blueprints" &&
					rootComponentId.value == "blueprints_root" &&
					isSharedBlueprintsEnabled.value &&
					!isEditingSharedBlueprint.value),
		);

	return Object.fromEntries(categoriesWithTools);
});

const searchCount = computed(() => {
	if (!query.value) return undefined;
	return Object.values(categories.value).reduce(
		(acc, v) => acc + v.length,
		0,
	);
});

const placeholder = computed(() => {
	if (activeToolkit.value == "core") return "Interface toolkit";
	if (activeToolkit.value == "blueprints") return "Blueprints toolkit";
	return "Toolkit";
});

function getRelevantToolsInCategory(categoryId: string) {
	if (categoryId === "Shared Blueprints") {
		// Don't show shared blueprints when editing a shared blueprint (no nesting for now)
		if (
			!isSharedBlueprintsEnabled.value ||
			isEditingSharedBlueprint.value
		) {
			return [];
		}
		// Read shared blueprints directly from component tree
		const enriched = sharedBlueprintsFromTree.value.map((blueprint) => {
			const name = blueprint.content?.key || "Untitled Blueprint";
			const description =
				blueprint.content?.description || "A shared blueprint";
			return {
				type: `blueprints_shared:${blueprint.id}`,
				name,
				description,
				category: "Shared Blueprints",
				sourceBlueprintId: blueprint.id,
			};
		});
		const q = query.value.toLocaleLowerCase();
		const queryApplied = enriched
			.filter((tool) => !q || tool.name.toLocaleLowerCase().includes(q))
			.sort((a, b) =>
				a.name.localeCompare(b.name, undefined, {
					sensitivity: "base",
				}),
			);

		return queryApplied;
	}

	const typeList = getSupportedComponentTypes().filter((type) => {
		const def = getComponentDefinition(type);
		if (type.startsWith("shared_")) return false;
		if (def.category != categoryId) return false;
		if (!def.toolkit && activeToolkit.value !== "core") return false;
		if (def.toolkit && def.toolkit !== activeToolkit.value) return false;
		if (def.deprecated) return false;
		// Filter out restricted blocks when editing a shared blueprint
		if (
			isEditingSharedBlueprint.value &&
			RESTRICTED_BLOCKS_IN_SHARED_BLUEPRINT.has(type)
		)
			return false;
		return true;
	});
	const enriched = typeList.map((type) => {
		const { name, description, category } = getComponentDefinition(type);
		return { type, name, description, category: category ?? "Other" };
	});
	const q = query.value.toLocaleLowerCase();
	const queryApplied = enriched
		.filter((tool) => !q || tool.name.toLocaleLowerCase().includes(q))
		.sort((a, b) =>
			a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
		);

	return queryApplied;
}

function handleDragStart(
	ev: DragEvent,
	type: Component["type"],
	sourceBlueprintId?: string,
) {
	wfbm.setSelection(null);
	// Embed sourceBlueprintId in the MIME type for shared blueprints
	const mimeType = sourceBlueprintId
		? `application/json;writer=blueprints_shared,${sourceBlueprintId}`
		: `application/json;writer=${type},`;
	ev.dataTransfer.setData(mimeType, "{}");
}

function handleDragEnd(ev: DragEvent) {
	removeInsertionCandidacy(ev);
}

function getToolIcons(tool: ReturnType<typeof getRelevantToolsInCategory>[0]) {
	// For shared blueprints from tree, use the Logic category icon
	if (tool.sourceBlueprintId) {
		return [`/components/blueprints_category_Logic.svg`].map((p) =>
			convertAbsolutePathtoFullURL(p),
		);
	}
	return [
		`/components/${tool.type}.svg`,
		`/components/${activeToolkit.value == "blueprints" ? "blueprints_" : ""}category_${tool.category}.svg`,
	].map((p) => convertAbsolutePathtoFullURL(p));
}

function handleDeleteSharedBlueprint(
	blueprintId: string,
	blueprintName: string,
) {
	if (
		!confirm(
			`Are you sure you want to delete the shared blueprint "${blueprintName}"?`,
		)
	) {
		return;
	}

	try {
		// Use removeComponentsSubtree for proper cleanup of dependencies and connections
		removeComponentsSubtree(blueprintId);
		pushToast({
			type: "success",
			message: `Shared blueprint '${blueprintName}' deleted.`,
		});
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to delete shared blueprint: ${error instanceof Error ? error.message : String(error)}`,
		});
	}
}

watch(activeToolkit, () => {
	query.value = "";
});
</script>

<style scoped>
.sharedBlueprintNotice {
	display: flex;
	align-items: flex-start;
	gap: 8px;
	padding: 12px;
	margin-bottom: 12px;
	background: var(--builderSubtleBackgroundColor, #f8fafc);
	border-radius: 6px;
	font-size: 12px;
	line-height: 1.4;
	color: var(--builderSecondaryTextColor);
}

.sharedBlueprintNotice :deep(svg) {
	flex-shrink: 0;
	margin-top: 1px;
}

.category .header {
	font-size: 12px;
	font-weight: 500;
	line-height: 12px; /* 100% */
	letter-spacing: 1.3px;
	text-transform: uppercase;
	color: var(--builderSecondaryTextColor);
	margin-bottom: 8px;
}

.tools {
	display: grid;
	grid-template-columns: 1fr;
	grid-template-rows: auto;
}

.tool {
	display: grid;
	grid-template-columns: 18px 1fr auto;
	grid-template-rows: 1fr;
	column-gap: 8px;
	padding: 8px;
	border-radius: 4px;
	cursor: grab;
	position: relative;
}

.tool--shared {
	grid-template-columns: 18px 1fr auto;
}

.tool img {
	max-width: 18px;
	max-height: 18px;
	aspect-ratio: 1 / 1;
}

.tool:hover {
	background: var(--builderSubtleSeparatorColor);
}

.tool__delete {
	display: none;
	align-items: center;
	justify-content: center;
	width: 20px;
	height: 20px;
	padding: 0;
	border: none;
	background: transparent;
	cursor: pointer;
	color: var(--builderSecondaryTextColor);
	border-radius: 4px;
	opacity: 0.6;
	transition:
		opacity 0.2s,
		background 0.2s;
}

.tool--shared:hover .tool__delete {
	display: flex;
}

.tool__delete:hover {
	opacity: 1;
	background: var(--builderSubtleSeparatorColor);
	color: var(--builderErrorColor);
}

.tool__delete:active {
	opacity: 0.8;
}

.BuilderSidebarPanel__footer__actions {
	flex: 0 0 var(--builderPanelSwitcherHeight);
	bottom: 0;
	height: var(--builderPanelSwitcherHeight);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 8px;
	border-top: 1px solid var(--builderSeparatorColor);
	background: var(--builderBackgroundColor);
	padding: 8px;
}

.BuilderSidebarPanel__footer__btn {
	font-size: 12px;
	font-weight: 500;
	line-height: 180%;
	min-width: 190px;
}
</style>
