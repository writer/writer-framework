<template>
	<div class="BuilderSidebarTree">
		<BuilderSidebarTitleSearch
			v-model="searchQuery"
			title="Component Tree"
			icon="account_tree"
			:disabled="!matchAvailable"
		>
			<i
				:class="{ disabled: !matchAvailable }"
				class="searchIcon material-symbols-outlined"
				:title="
					matchAvailable
						? `Go to match ${previousMatchIndex + 1} of ${matchingComponents.length}`
						: `Previous match`
				"
				tabindex="0"
				@keydown.enter="goToPreviousMatch"
				@click="goToPreviousMatch"
			>
				navigate_before
			</i>
			<i
				:class="{ disabled: !matchAvailable }"
				class="searchIcon material-symbols-outlined"
				:title="
					matchAvailable
						? `Go to match ${nextMatchIndex + 1} of ${matchingComponents.length}`
						: `Next match`
				"
				tabindex="0"
				@keydown.enter="goToNextMatch"
				@click="goToNextMatch"
			>
				navigate_next
			</i>
		</BuilderSidebarTitleSearch>
		<div ref="componentTree" class="components">
			<div
				v-for="component in rootComponents"
				:key="component.id"
				class="selector"
			>
				<BuilderTreeBranch
					:component-id="component.id"
					:matching-components="matchingComponents"
				></BuilderTreeBranch>
			</div>
		</div>
		<div class="add">
			<button v-if="rootType == 'root'" @click="addPage">
				<i class="material-symbols-outlined"> add </i>
				Add Page
			</button>
			<button v-if="rootType == 'workflows_root'" @click="addWorkflow">
				<i class="material-symbols-outlined"> add </i>
				Add Workflow
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, nextTick, ref, Ref, ComputedRef } from "vue";
import { useComponentActions } from "./useComponentActions";
import BuilderTreeBranch from "./BuilderTreeBranch.vue";
import injectionKeys from "../injectionKeys";
import { Component } from "@/writerTypes";
import { watch } from "vue";
import BuilderSidebarTitleSearch from "./BuilderSidebarTitleSearch.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { createAndInsertComponent, goToComponentParentPage } =
	useComponentActions(wf, ssbm);

const searchQuery: Ref<string> = ref(null);
const matchIndex: Ref<number> = ref(-1);
const rootType = computed(() => {
	let targetType = "root";
	if (ssbm.getMode() == "workflows") {
		targetType = "workflows_root";
	}
	return targetType;
});
const rootComponents = computed(() => {
	return wf
		.getComponents(null, { sortedByPosition: true })
		.filter((c) => c.type == rootType.value);
});

function determineMatch(component: Component, query: string): boolean {
	if (component.id.toLocaleLowerCase().includes(query)) return true;
	if (component.type.toLocaleLowerCase().includes(query)) return true;
	const typeName = wf.getComponentDefinition(component.type)?.name;
	if (typeName.includes(query)) return true;
	const fields = [
		...Object.values(component.content ?? {}),
		...Object.values(component.handlers ?? {}),
		...Object.values(component.binding ?? {}),
	];
	for (let i = 0; i < fields.length; i++) {
		const fieldValue = fields[i]?.toString().toLocaleLowerCase();
		if (fieldValue?.includes(query)) return true;
	}
	return false;
}

async function selectMatch() {
	const component = matchingComponents.value?.[matchIndex.value];
	if (!component) return;
	goToComponentParentPage(component.id);
	await nextTick();
	ssbm.setSelection(component.id);
}

const previousMatchIndex = computed(() => {
	if (!matchAvailable.value) return -1;
	let i = matchIndex.value - 1;
	if (i < 0) {
		i = matchingComponents.value.length - 1;
	}
	return i;
});

const nextMatchIndex = computed(() => {
	if (!matchAvailable.value) return -1;
	let i = matchIndex.value + 1;
	if (i > matchingComponents.value.length - 1) {
		i = 0;
	}
	return i;
});

function goToPreviousMatch() {
	matchIndex.value = previousMatchIndex.value;
	selectMatch();
}

function goToNextMatch() {
	matchIndex.value = nextMatchIndex.value;
	selectMatch();
}

const matchingComponents: ComputedRef<Component[]> = computed(() => {
	if (!searchQuery.value) return;
	const query = searchQuery.value.toLocaleLowerCase();
	const components = wf.getComponents();
	const matching = components.filter((c) => determineMatch(c, query));
	return matching;
});

watch(matchingComponents, () => {
	matchIndex.value = -1;
});

const matchAvailable: ComputedRef<boolean> = computed(
	() => matchingComponents.value?.length > 0,
);

async function addPage() {
	const pageId = createAndInsertComponent("page", "root");
	wf.setActivePageId(pageId);
	await nextTick();
	ssbm.setSelection(pageId);
}

async function addWorkflow() {
	const pageId = createAndInsertComponent(
		"workflows_workflow",
		"workflows_root",
	);
	wf.setActivePageId(pageId);
	await nextTick();
	ssbm.setSelection(pageId);
}
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebarTree {
	user-select: none;
	position: relative;
	display: flex;
	flex-direction: column;
}

.searchIcon.disabled {
	color: var(--builderDisabledColor);
}

.components {
	padding: 0 12px 12px 12px;
}

.add {
	margin-top: auto;
	padding: 0 16px 16px 16px;
}
</style>
