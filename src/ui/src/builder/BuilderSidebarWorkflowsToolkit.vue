<template>
	<div class="BuilderSidebarWorkflowsToolkit">
		<div class="sectionTitle">
			<i class="material-symbols-outlined"> handyman </i>
			<h3>Workflows Toolkit</h3>
		</div>
		<div class="categories">
			<template
				v-for="(categoryData, category) in categoriesData"
				:key="category"
			>
				<div v-if="categoryData.isVisible !== false" class="category">
					<div class="title">
						<i class="material-symbols-outlined">{{
							categoryData.icon ?? "question_mark"
						}}</i>
						<h4>{{ category }}</h4>

						<div
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
						</div>
					</div>

					<div v-show="!categoryData.isCollapsed" class="components">
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
import injectionKeys from "../injectionKeys";
import nodeTemplateDefs from "./workflows/nodeTemplateDefs";

const wf = inject(injectionKeys.core);

type CategoryData = {
	isVisible?: boolean;
	isCollapsed?: boolean;
	icon?: string;
};

const categoriesData: Ref<Record<string, CategoryData>> = ref({
	Content: {
		icon: "toc",
		isCollapsed: false,
	},
});

function toggleCollapseCategory(categoryId: string) {
	const categoryData = categoriesData.value[categoryId];
	categoryData.isCollapsed = !categoryData.isCollapsed;
}

const definitionsByDisplayCategory = computed(() => {
	const types = Object.keys(nodeTemplateDefs);
	const result: Record<string, Record<string, any>> = {};

	types.map((type) => {
		const definition = nodeTemplateDefs[type];
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

const handleDragStart = (ev: DragEvent, type: string) => {
	ev.dataTransfer.setData(
		`application/json;writer=node`,
		JSON.stringify({ type }),
	);
};

const handleDragEnd = (ev: DragEvent) => {};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebarWorkflowsToolkit {
	font-size: 0.7rem;
}

.BuilderSidebarWorkflowsToolkit > .sectionTitle {
	padding: 16px;
	position: sticky;
	top: 0;
	background: var(--builderBackgroundColor);
	font-size: 0.875rem;
	height: 40px;
}

h3 {
	font-weight: 500;
	font-size: 0.875rem;
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
}
</style>
