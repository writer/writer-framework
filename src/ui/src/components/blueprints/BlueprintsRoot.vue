<template>
	<div ref="rootEl" class="BlueprintsRoot" data-writer-container>
		<template v-for="vnode in getChildrenVNodes()" :key="vnode.key">
			<component
				:is="vnode"
				v-if="vnode.key === `${displayedBlueprintId}:0`"
			></component>
		</template>
	</div>
</template>

<script lang="ts">
const description =
	"The root component of the application, which serves as the starting point of the component hierarchy.";

export default {
	writer: {
		name: "Blueprints Root",
		toolkit: "blueprints",
		category: "Root",
		description,
		allowedChildrenTypes: ["blueprints_blueprint"],
		fields: {},
	},
};
</script>
<script setup lang="ts">
import { computed, inject, useTemplateRef } from "vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);
const rootEl = useTemplateRef("rootEl");

const displayedBlueprintId = computed(() => {
	const activePageId = wf.activePageId.value;
	const activePageExists = Boolean(wf.getComponentById(activePageId));
	if (activePageExists && wf.isChildOf("blueprints_root", activePageId))
		return activePageId;

	const pageComponents = wf.getComponents("blueprints_root", {
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

.BlueprintsRoot {
	background: var(--emptinessColor);
	min-height: 100%;
	display: flex;
	width: 100%;
}

.BlueprintsRoot.selected {
	background-color: var(--emptinessColor);
}
</style>
