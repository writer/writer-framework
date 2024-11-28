<template>
	<BuilderSidebarPanel
		v-model="query"
		class="BuilderSidebarComponentTree"
		placeholder="Component tree"
	>
		<BuilderSidebarComponentTreeBranch
			class="rootBranch"
			:component-id="rootComponentId"
			:query="query"
			:is-root="true"
		></BuilderSidebarComponentTreeBranch>
	</BuilderSidebarPanel>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import BuilderSidebarPanel from "./BuilderSidebarPanel.vue";
import injectionKeys from "@/injectionKeys";
import BuilderSidebarComponentTreeBranch from "./BuilderSidebarComponentTreeBranch.vue";

const wfbm = inject(injectionKeys.builderManager);
const query = ref("");

const rootComponentId = computed(() => {
	if (wfbm.getMode() == "workflows") {
		return "workflows_root";
	}
	return "root";
});
</script>

<style scoped>
.BuilderSidebarComponentTree {
	display: flex;
	flex-direction: column;
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
}

.tools {
	display: grid;
	grid-template-columns: 24px 1fr;
	grid-template-rows: auto;
	padding: 0 8px 0 8px;
	row-gap: 12px;
	column-gap: 4px;
}
</style>
