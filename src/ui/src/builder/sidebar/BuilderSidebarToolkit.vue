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
					v-for="tool in tools"
					:key="tool.type"
					class="tool"
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
					/>
					<div class="name">{{ tool.name }}</div>
				</div>
			</div>
		</div>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { computed, inject, ref, watch } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import {
	getComponentDefinition,
	getSupportedComponentTypes,
} from "@/core/templateMap";
import injectionKeys from "@/injectionKeys";
import { useDragDropComponent } from "../useDragDropComponent";
import { Component } from "@/writerTypes";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { removeInsertionCandidacy } = useDragDropComponent(wf);
const query = ref("");

const displayedCategories = [
	"Layout",
	"Content",
	"Input",
	"Embed",
	"Writer",
	"Logic",
	"Triggers",
	"Other",
];

const activeToolkit = computed(() => {
	if (wfbm.getMode() == "workflows") {
		return "workflows";
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
		.filter(([_categoryId, tools]) => tools.length > 0);

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
	if (activeToolkit.value == "core") return "Core toolkit";
	if (activeToolkit.value == "workflows") return "Workflows toolkit";
	return "Toolkit";
});

function getRelevantToolsInCategory(categoryId: string) {
	const typeList = getSupportedComponentTypes().filter((type) => {
		const def = getComponentDefinition(type);
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
	const queryApplied = enriched.filter(
		(tool) => !q || tool.name.toLocaleLowerCase().includes(q),
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
		`/components/${activeToolkit.value == "workflows" ? "workflows_" : ""}category_${tool.category}.svg`,
	].map((p) => convertAbsolutePathtoFullURL(p));
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
	grid-template-columns: 18px 1fr;
	grid-template-rows: 1fr;
	column-gap: 8px;
	padding: 8px;
	border-radius: 4px;
	cursor: grab;
}

.tool img {
	max-width: 18px;
	max-height: 18px;
	aspect-ratio: 1 / 1;
}

.tool:hover {
	background: var(--builderSubtleSeparatorColor);
}
</style>
