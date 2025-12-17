<template>
	<div class="BlueprintsRoot" data-writer-container>
		<div
			v-if="displayedBlueprintId || displayedBlueprintKey"
			class="BlueprintsRoot_titleContainer"
		>
			<span class="BlueprintsRoot_title_prefix">Blueprint:</span>
			<div>
				{{
					displayedBlueprintKey
						? displayedBlueprintKey
						: displayedBlueprintId
				}}
			</div>
		</div>
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
import { computed, inject, onMounted } from "vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);

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

const displayedBlueprintKey = computed(() => {
	const displayedBlueprint = wf.getComponentById(displayedBlueprintId.value);
	return displayedBlueprint?.content?.key;
});

onMounted(() => {
	if (
		displayedBlueprintId.value &&
		wf.activePageId.value !== displayedBlueprintId.value
	) {
		wf.setActivePageId(displayedBlueprintId.value);
	}
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

.BlueprintsRoot_titleContainer {
	position: absolute;
	top: 24px;
	left: 24px;
	font-family: Poppins, "Helvetica Neue", "Lucida Grande", sans-serif;
	font-size: 10px;
	font-weight: 500;
	line-height: 10px; /* 100% */
	letter-spacing: 0.5px;
	text-transform: none;
	z-index: 1;
	pointer-events: none;
	user-select: none;

	background: var(--builderSubtleSeparatorColor);
	padding: 8px;
	border-radius: 8px;
	border: 1px solid var(--builderSeparatorColor);
	display: flex;
	align-items: baseline;
	gap: 4px;
}

.BlueprintsRoot_title_prefix {
	text-transform: none;
	color: var(--builderSecondaryTextColor);
}

.BlueprintsRoot.selected {
	background-color: var(--emptinessColor);
}
</style>
