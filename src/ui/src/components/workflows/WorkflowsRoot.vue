<template>
	<div ref="rootEl" class="WorkflowsRoot" data-writer-container>
		<template v-for="vnode in getChildrenVNodes()" :key="vnode.key">
			<component
				:is="vnode"
				v-if="vnode.key === `${displayedWorkflowId}:0`"
			></component>
		</template>
	</div>
</template>

<script lang="ts">
const description =
	"The root component of the application, which serves as the starting point of the component hierarchy.";

export default {
	writer: {
		name: "Workflows Root",
		toolkit: "workflows",
		category: "Root",
		description,
		allowedChildrenTypes: ["workflows_workflow"],
		fields: {},
	},
};
</script>
<script setup lang="ts">
import { computed, inject, ref, Ref } from "vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);
const rootEl: Ref<HTMLElement> = ref(null);

const displayedWorkflowId = computed(() => {
	const activePageId = wf.activePageId.value;
	const activePageExists = Boolean(wf.getComponentById(activePageId));
	if (activePageExists && wf.isChildOf("workflows_root", activePageId))
		return activePageId;

	const pageComponents = wf.getComponents("workflows_root", {
		includeBMC: true,
		includeCMC: false,
		sortedByPosition: true,
	});
	if (pageComponents.length == 0) return null;

	return pageComponents[0].id;
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.WorkflowsRoot {
	background: var(--emptinessColor);
	min-height: 100%;
	display: flex;
	width: 100%;
}

.WorkflowsRoot.selected {
	background-color: var(--emptinessColor);
}
</style>
