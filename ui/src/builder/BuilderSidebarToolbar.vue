<template>
	<div class="BuilderSidebarToolbar">
		<div class="sectionTitle">
			<i class="ri-tools-line ri-xl"></i>
			<h3>Toolkit</h3>
		</div>
		<div class="tools">
			<template
				v-for="(categoryData, category) in categoriesData"
				:key="category"
			>
				<div class="category" v-if="categoryData.isVisible !== false">
					<div class="title">
						<i :class="categoryData.icon ?? 'ri-question-line'"></i>
						<h4>{{ category }}</h4>
					</div>
					<div
						v-for="(
							definition, type
						) in definitionsByDisplayCategory[category]"
						:key="type"
						class="tool button"
						:title="definition.description"
						draggable="true"
						:data-component-type="type"
						v-on:dragend="handleDragEnd($event)"
						v-on:dragstart="handleDragStart($event, type)"
					>
						{{ definition.name ?? type }}
					</div>
				</div>
			</template>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useDragDropComponent } from "./useDragDropComponent";
import injectionKeys from "../injectionKeys";
import { Component, StreamsyncComponentDefinition } from "../streamsyncTypes";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { removeInsertionCandidacy } = useDragDropComponent(ss);

type CategoryData = {
	isVisible?: boolean;
	icon?: string;
};

const categoriesData: Record<string, CategoryData> = {
	Root: {
		isVisible: false,
	},
	Layout: {
		icon: "ri-layout-line",
	},
	Content: {
		icon: "ri-image-line",
	},
	Input: {
		icon: "ri-keyboard-line",
	},
	Other: {
		icon: "ri-flow-chart",
	},
};

const definitionsByDisplayCategory = computed(() => {
	const types = ss.getSupportedComponentTypes();
	const result: Record<
		string,
		Record<string, StreamsyncComponentDefinition>
	> = {};

	types.map((type) => {
		const definition = ss.getComponentDefinition(type);
		const isMatch = Object.keys(categoriesData).includes(
			definition.category
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
	ev.dataTransfer.setData(`application/json;streamsync=${type},`, "{}");
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

.BuilderSidebarToolbar > .sectionTitle {
	padding: 16px;
	position: sticky;
	top: 0;
	background: var(--builderBackgroundColor);
}

.tools {
	padding: 0 12px 12px 12px;
	flex: 1 1 auto;
	display: flex;
	flex-direction: column;
}

.category .title {
	display: flex;
	align-items: center;
	padding: 12px 8px 12px 8px;
}

.category .title i {
	margin-right: 8px;
}

.tool {
	padding: 8px;
	border-radius: 4px;
	cursor: move;
	cursor: grab;
}

.tool:hover {
	background: var(--builderSubtleHighlightColor);
}
</style>
