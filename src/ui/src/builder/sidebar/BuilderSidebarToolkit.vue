<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarToolkit"
		:placeholder="placeholder"
		:search-count="searchCount"
	>
		<div
			v-for="(tools, categoryId) in categories"
			:key="categoryId"
			class="category"
		>
			<div class="header">{{ categoryId }}</div>
			<div class="tools">
				<div
					v-if="
						categoryId === 'Custom Blocks' &&
						rootComponentId == 'blueprints_root' &&
						isCustomBlocksEnabled
					"
					class="tool tool--create"
					@click="showCreateCustomBlock"
				>
					<WdsIcon name="plus" />
					<div class="name">Create Custom Block</div>
				</div>
				<!-- Block Library button for Custom Blocks category -->
				<div
					v-if="
						categoryId === 'Custom Blocks' &&
						rootComponentId == 'blueprints_root' &&
						isCustomBlocksEnabled
					"
					class="tool tool--create"
					@click="showBlockLibrary"
				>
					<WdsIcon name="folder" />
					<div class="name">Block Library</div>
				</div>
				<div
					v-for="tool in tools"
					:key="tool.type"
					class="tool"
					:class="{
						'tool--custom':
							categoryId === 'Custom Blocks' &&
							isCustomBlocksEnabled,
					}"
					:data-writer-tooltip="tool.description"
					data-writer-tooltip-placement="right"
					data-writer-tooltip-gap="8"
					draggable="true"
					:data-component-type="tool.type"
					@dragend="handleDragEnd($event)"
					@dragstart="handleDragStart($event, tool.type)"
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
							categoryId === 'Custom Blocks' &&
							isCustomBlocksEnabled
						"
						class="tool__delete"
						:data-writer-tooltip="`Delete ${tool.name}`"
						data-writer-tooltip-placement="right"
						@click.stop="handleDeleteBlock(tool.type, tool.name)"
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
	<BuilderSettingsCustomBlock
		v-if="isCreateCustomBlockModalShown && isCustomBlocksEnabled"
		v-model="isCreateCustomBlockModalShown"
	/>
	<BuilderBlockLibraryPanel
		v-if="isCustomBlocksEnabled"
		v-model="isBlockLibraryModalShown"
	/>
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
import BuilderSettingsCustomBlock from "../settings/BuilderSettingsCustomBlock.vue";
import { useToasts } from "../useToast";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BuilderBlockLibraryPanel = defineAsyncComponentWithLoader({
	loader: () => import("../panels/BuilderBlockLibraryPanel.vue"),
});

const { pushToast } = useToasts();

const isAutogenModalShown = inject(
	injectionKeys.isAutogenModalShown,
	ref(false),
);
function showAutogen() {
	isAutogenModalShown.value = true;
}

const isCreateCustomBlockModalShown = ref(false);
function showCreateCustomBlock() {
	isCreateCustomBlockModalShown.value = true;
}

const isBlockLibraryModalShown = ref(false);
function showBlockLibrary() {
	isBlockLibraryModalShown.value = true;
}

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { removeInsertionCandidacy } = useDragDropComponent(wf);
const query = ref("");

const isCustomBlocksEnabled = computed(
	() =>
		Array.isArray(wf.featureFlags.value) &&
		wf.featureFlags.value.includes("custom_blocks"),
);

const rootComponentId = wfbm.activeRootId;

const displayedCategories = [
	"Layout",
	"Content",
	"Input",
	"Embed",
	"Writer",
	"Logic",
	"Triggers",
	"Other",
	"Custom Blocks",
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
				(categoryId === "Custom Blocks" &&
					rootComponentId.value == "blueprints_root" &&
					isCustomBlocksEnabled.value),
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
	if (categoryId === "Custom Blocks") {
		if (!isCustomBlocksEnabled.value) {
			return [];
		}
		const typeList = getSupportedComponentTypes().filter((type) => {
			if (!type.startsWith("custom_")) return false;
			const def = getComponentDefinition(type);
			if (!def.toolkit && activeToolkit.value !== "core") return false;
			if (def.toolkit && def.toolkit !== activeToolkit.value)
				return false;
			if (def.deprecated) return false;
			return true;
		});
		const enriched = typeList.map((type) => {
			const { name, description } = getComponentDefinition(type);
			return { type, name, description, category: "Custom Blocks" };
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
		if (type.startsWith("custom_")) return false;
		if (def.category != categoryId) return false;
		if (!def.toolkit && activeToolkit.value !== "core") return false;
		if (def.toolkit && def.toolkit !== activeToolkit.value) return false;
		if (def.deprecated) return false;
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

function handleDragStart(ev: DragEvent, type: Component["type"]) {
	wfbm.setSelection(null);
	ev.dataTransfer.setData(`application/json;writer=${type},`, "{}");
}

function handleDragEnd(ev: DragEvent) {
	removeInsertionCandidacy(ev);
}

function getToolIcons(tool: ReturnType<typeof getRelevantToolsInCategory>[0]) {
	return [
		`/components/${tool.type}.svg`,
		`/components/${activeToolkit.value == "blueprints" ? "blueprints_" : ""}category_${tool.category}.svg`,
	].map((p) => convertAbsolutePathtoFullURL(p));
}

async function handleDeleteBlock(blockType: string, blockName: string) {
	if (
		!confirm(
			`Are you sure you want to delete the custom block "${blockName}"?`,
		)
	) {
		return;
	}

	try {
		const response = await fetch(`/api/custom-blocks/${blockType}`, {
			method: "DELETE",
		});

		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({ detail: "Failed to delete block" }));
			throw new Error(error.detail || "Failed to delete block");
		}

		pushToast({
			type: "success",
			message: `Custom block '${blockName}' deleted.`,
		});
		await wf.init();
	} catch (error) {
		pushToast({
			type: "error",
			message: `Failed to delete block: ${error instanceof Error ? error.message : String(error)}`,
		});
	}
}

watch(activeToolkit, () => {
	query.value = "";
});
</script>

<style scoped>
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

.tool--custom {
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

.tool--create {
	cursor: pointer;
	opacity: 0.8;
}

.tool--create:hover {
	opacity: 1;
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

.tool--custom:hover .tool__delete {
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
