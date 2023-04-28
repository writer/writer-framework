<template>
	<div class="BuilderSidebarTree">
		<div class="sectionTitle">
			<i class="ri-node-tree ri-xl"></i>
			<h3>Component Tree</h3>
		</div>
		<div class="components" ref="componentTree">
			<div
				class="selector"
				v-for="component in rootComponents"
				:key="component.id"
			>
				<BuilderTreeBranch
					:component-id="component.id"
				></BuilderTreeBranch>
			</div>
		</div>
		<div class="addPage">
			<button v-on:click="addPage">
				<i class="ri-add-line"></i>Add Page
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, nextTick } from "vue";
import { useComponentActions } from "./useComponentActions";
import BuilderTreeBranch from "./BuilderTreeBranch.vue";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { createAndInsertComponent } = useComponentActions(ss, ssbm);

const rootComponents = computed(() => {
	return ss.getComponents(null, true);
});

async function addPage() {
	const pageId = createAndInsertComponent("page", "root");
	ss.setActivePageId(pageId);
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

.sectionTitle {
	background: var(--builderBackgroundColor);
	padding: 16px;
	top: 0;
	position: sticky;
}

.components {
	padding: 0 12px 12px 12px;
}

.addPage {
	margin-top: auto;
	padding: 0 16px 16px 16px;
}
</style>
