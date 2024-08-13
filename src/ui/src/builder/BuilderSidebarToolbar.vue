<template>
	<div class="BuilderSidebarToolbar">
		<BuilderSidebarTitleSearch
			v-model="searchQuery"
			title="Toolkit"
			icon="handyman"
		/>
		<div class="categories">
			<template
				v-for="(categoryData, category) in categoriesData"
				:key="category"
			>
				<div v-if="shouldDisplayCategory(category)" class="category">
					<div class="title">
						<i class="material-symbols-outlined">{{
							categoryData.icon ?? "question_mark"
						}}</i>
						<h4>{{ category }}</h4>

						<button
							class="drop-arrow"
							@click="toggleCollapseCategory(category)"
						>
							<i class="material-symbols-outlined">
								{{
									categoryData.isCollapsed
										? "expand_more"
										: "expand_less"
								}}
							</i>
						</button>
					</div>

					<div
						v-show="!categoryData.isCollapsed"
						class="components"
						:aria-expanded="!categoryData.isCollapsed"
					>
						<div
							v-for="(
								definition, type
							) in definitionsByDisplayCategory[category]"
							:key="type"
							class="component button"
							:title="definition.description"
							draggable="true"
							:data-component-type="type"
							@dragend="handleDragEnd($event)"
							@dragstart="handleDragStart($event, type)"
						>
							{{ definition.name ?? type }}
							<i
								v-if="type.startsWith('custom_')"
								class="material-symbols-outlined"
								title="(Custom component template)"
								>manga</i
							>
						</div>
					</div>
				</div>
			</template>
		</div>
	</div>
</template>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import { useDragDropComponent } from "./useDragDropComponent";
import injectionKeys from "../injectionKeys";
import { Component, WriterComponentDefinition } from "../writerTypes";
import BuilderSidebarTitleSearch from "./BuilderSidebarTitleSearch.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { removeInsertionCandidacy } = useDragDropComponent(wf);

type CategoryId = "Root" | "Layout" | "Content" | "Input" | "Embed" | "Other";

type CategoryData = {
	isVisible?: boolean;
	isCollapsed?: boolean;
	icon?: string;
};

const searchQuery = ref("");

const categoriesData: Ref<Record<CategoryId, CategoryData>> = ref({
	Root: {
		isVisible: false,
	},
	Layout: {
		icon: "space_dashboard",
		isCollapsed: false,
	},
	Content: {
		icon: "toc",
		isCollapsed: false,
	},
	Input: {
		icon: "input",
		isCollapsed: false,
	},
	Embed: {
		icon: "integration_instructions",
		isCollapsed: false,
	},
	Other: {
		icon: "dynamic_feed",
		isCollapsed: false,
	},
});

function shouldDisplayCategory(categoryId: CategoryId): boolean {
	if (categoriesData.value[categoryId]?.isVisible === false) return false;

	return (
		Object.keys(definitionsByDisplayCategory.value[categoryId] ?? {})
			.length > 0
	);
}

function toggleCollapseCategory(categoryId: string) {
	const categoryData = categoriesData.value[categoryId];
	categoryData.isCollapsed = !categoryData.isCollapsed;
}

const definitionsByDisplayCategory = computed(() => {
	const types = wf.getSupportedComponentTypes();
	const result: Partial<
		Record<CategoryId, Record<string, WriterComponentDefinition>>
	> = {};

	types.map((type) => {
		const definition = wf.getComponentDefinition(type);

		const matchingSearch =
			searchQuery.value === "" ||
			definition.name
				.toLocaleLowerCase()
				.includes(searchQuery.value.toLocaleLowerCase());

		if (!matchingSearch) return;

		const isMatch = Object.keys(categoriesData.value).includes(
			definition.category,
		);
		let displayCategory: string;
		if (!isMatch) {
			displayCategory = "Other";
		} else {
			displayCategory = definition.category;
		}
		if (!result[displayCategory]) {
			result[displayCategory] = {};
		}
		result[displayCategory][type] = definition;
	});

	return result;
});

const handleDragStart = (ev: DragEvent, type: Component["type"]) => {
	ssbm.setSelection(null);
	ev.dataTransfer.setData(`application/json;writer=${type},`, "{}");
};

const handleDragEnd = (ev: DragEvent) => {
	removeInsertionCandidacy(ev);
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebarToolbar {
	font-size: 0.7rem;
}

.categories {
	padding: 0 12px 12px 12px;
	flex: 1 1 auto;
	display: flex;
	flex-direction: column;
}

.category .title {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 8px;
	gap: 8px;
}

.category .title h4 {
	flex: 1 0 auto;
}

.category .components {
	padding: 4px 0 4px 0;
}

.component {
	padding: 8px;
	border-radius: 4px;
	cursor: grab;
	display: flex;
	align-items: center;
	gap: 4px;
	height: 33px;
}

.component:hover {
	background: var(--builderSubtleHighlightColor);
}

.drop-arrow {
	/* reset button default */
	border: none;
	background-color: unset;
	padding: 0;
	margin: 0;
	height: auto;
	width: auto;

	border-radius: 50%;
	min-width: 24px;
	min-height: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
}

.drop-arrow:hover {
	background: var(--builderSubtleSeparatorColor);
	color: unset;
}
</style>
