<template>
	<div ref="rootEl" class="WorkflowsRoot" data-writer-container>
		Workflows root: {{ isRootActive }}
		<template v-for="(vnode, index) in getChildrenVNodes()" :key="index">
			<component
				:is="vnode"
				v-if="vnode.key === `${activePageId}:0`"
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
		allowedChildrenTypes: ["workflow"],
		fields: {},
	},
};
</script>
<script setup lang="ts">
import { computed, inject, ref, Ref, watch, onBeforeMount } from "vue";
import injectionKeys from "@/injectionKeys";

const importedModulesSpecifiers: Record<string, string> = {};
const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);
const rootEl: Ref<HTMLElement> = ref(null);
const { isComponentVisible } = useEvaluator(wf);

const activePageId = computed(() => wf.getActivePageId());
const isRootActive = computed(() => {
	if (!activePageId.value) return false;
	return wf.isChildOf("workflowsroot", activePageId.value);
});

watch(activePageId, (newPageId) => {
	if (!wf.isChildOf("workflowsroot", newPageId)) return;

	const page = wf.getComponentById(newPageId);
	const pageKey = page.content?.["key"];
	if (ssbm && ssbm.getSelectedId() !== newPageId) {
		ssbm.setSelection(null);
	}
	nextTick().then(() => {
		window.scrollTo(0, 0);
		const rendererEl = document.querySelector(".ComponentRenderer");
		rendererEl.parentElement.scrollTo(0, 0);
	});
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
