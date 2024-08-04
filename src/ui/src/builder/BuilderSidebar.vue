<template>
	<div class="BuilderSidebar">
		<template v-if="builderMode == 'workflows'">
			<BuilderSidebarWorkflowsToolkit></BuilderSidebarWorkflowsToolkit>
		</template>
		<template v-else>
			<BuilderSidebarToolbar class="toolbar"></BuilderSidebarToolbar>
			<BuilderSidebarTree class="tree"></BuilderSidebarTree>
		</template>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import BuilderSidebarToolbar from "./BuilderSidebarToolbar.vue";
import BuilderSidebarWorkflowsToolkit from "./BuilderSidebarWorkflowsToolkit.vue";
import BuilderSidebarTree from "./BuilderSidebarTree.vue";
import injectionKeys from "../injectionKeys";

const ssbm = inject(injectionKeys.builderManager);
const builderMode = computed(() => ssbm.getMode());
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebar {
	display: flex;
	flex-direction: column;
	height: 100%;
}

.toolbar {
	position: relative;
	height: 50%;
	display: flex;
	flex-direction: column;
	overflow-y: scroll;
}

.tree {
	height: 50%;
	overflow-y: auto;
	border-top: 1px solid var(--builderSeparatorColor);
}
</style>
