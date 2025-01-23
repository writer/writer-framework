<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarComponentTree"
		placeholder="Component tree"
	>
		<div>
			<BuilderSidebarComponentTreeBranch
				class="rootBranch"
				:component-id="rootComponentId"
				:query="query"
			></BuilderSidebarComponentTreeBranch>
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
					<i class="material-symbols-outlined"> add </i> Add
					page</WdsButton
				>
				<WdsButton
					v-if="rootComponentId == 'workflows_root'"
					variant="special"
					size="small"
					data-automation-action="add-workflow"
					@click="addWorkflow"
				>
					<i class="material-symbols-outlined"> add </i> Add
					workflow</WdsButton
				>
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
import { useComponentActions } from "../useComponentActions";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const query = ref("");

const { createAndInsertComponent } = useComponentActions(wf, wfbm);

const rootComponentId = computed(() => {
	if (wfbm.getMode() == "workflows") {
		return "workflows_root";
	}
	return "root";
});

async function addPage() {
	const pageId = createAndInsertComponent("page", "root");
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
}

async function addWorkflow() {
	const pageId = createAndInsertComponent(
		"workflows_workflow",
		"workflows_root",
	);
	wf.setActivePageId(pageId);
	await nextTick();
	wfbm.setSelection(pageId);
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
	margin-top: -8px;
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
	flex: 0 0 48px;
	bottom: 0;
	height: 48px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-top: 1px solid var(--builderSeparatorColor);
	background: var(--builderBackgroundColor);
}
</style>
