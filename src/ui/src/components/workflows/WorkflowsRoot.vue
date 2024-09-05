<template>
	<div ref="rootEl" class="WorkflowsRoot" data-writer-container>
		<template v-for="(vnode, index) in getChildrenVNodes()" :key="index">
			<component
				:is="vnode"
				v-if="vnode.key === `${displayedWorkflowId}:0`"
			></component>
		</template>
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { nextTick } from "vue";
import { useEvaluator } from "@/renderer/useEvaluator";

const description =
	"The root component of the application, which serves as the starting point of the component hierarchy.";

export default {
	writer: {
		name: "Root (Workflows)",
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
const ssbm = inject(injectionKeys.builderManager);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);
const rootEl: Ref<HTMLElement> = ref(null);

const displayedWorkflowId = computed(() => {
	const activePageId = wf.getActivePageId();
	if (activePageId && wf.isChildOf("workflows_root", activePageId))
		return activePageId;

	const pageComponents = wf.getComponents("workflows_root", {
		includeBMC: true,
		includeCMC: true,
		sortedByPosition: true,
	});
	if (pageComponents.length == 0) return null;
	return pageComponents[0].id;
});

// watch(activePageId, (newPageId) => {
// 	const page = wf.getComponentById(newPageId);
// 	const pageKey = page.content?.["key"];
// 	if (ssbm && ssbm.getSelectedId() !== newPageId) {
// 		ssbm.setSelection(null);
// 	}
// 	nextTick().then(() => {
// 		window.scrollTo(0, 0);
// 		const rendererEl = document.querySelector(".ComponentRenderer");
// 		rendererEl.parentElement.scrollTo(0, 0);
// 	});
// });
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
