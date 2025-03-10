<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import { Component } from "@/writerTypes";
import { inject, PropType } from "vue";

defineProps({
	blocks: { type: Array as PropType<Component[]>, required: true },
});

defineEmits({
	jumpToComponent: (componentId: string) => typeof componentId === "string",
	runBranch: (componentId: string) => typeof componentId === "string",
});

const wf = inject(injectionKeys.core);

function getBlockType(component: Component) {
	const def = wf.getComponentDefinition(component.type);
	return def?.name ?? component.type;
}

function getBlockTitle(component: Component) {
	return component.content?.alias || getBlockType(component);
}
</script>

<template>
	<div class="WorkflowToolbarBlocksDropdown">
		<p class="WorkflowToolbarBlocksDropdown__header">Start workflow from</p>
		<div class="WorkflowToolbarBlocksDropdown__list">
			<div
				v-for="startBlock of blocks"
				:key="startBlock.id"
				class="WorkflowToolbarBlocksDropdown__list__item"
			>
				<WdsButton
					variant="primary"
					size="smallIcon"
					custom-size="20px"
					data-writer-tooltip="Run the branch"
					@click="$emit('runBranch', startBlock.id)"
				>
					<i class="material-symbols-outlined">play_arrow</i>
				</WdsButton>
				<div>
					<p
						class="WorkflowToolbarBlocksDropdown__list__item__description"
					>
						{{ getBlockType(startBlock) }}
					</p>
					<p class="WorkflowToolbarBlocksDropdown__list__item__title">
						{{ getBlockTitle(startBlock) }}
					</p>
				</div>
				<WdsButton
					variant="neutral"
					size="smallIcon"
					custom-size="20px"
					data-writer-tooltip="Jump to the workflow"
					@click="$emit('jumpToComponent', startBlock.id)"
				>
					<i class="material-symbols-outlined">jump_to_element</i>
				</WdsButton>
			</div>
		</div>
	</div>
</template>

<style lang="css" scoped>
.WorkflowToolbarBlocksDropdown {
	border: 1px solid var(--wdsColorGray2);
	border: none;
	background: #fff;
	z-index: 2;
	width: 100%;
	max-height: 40vh;
	overflow-y: auto;
	border-radius: 8px;

	padding: 8px 10px;

	box-shadow: var(--wdsShadowMenu);
	box-sizing: border-box;

	max-height: 300px;
	overflow-y: auto;
}
.WorkflowToolbarBlocksDropdown__header {
	color: var(--wdsColorGray6);
	font-size: 12px;
	text-transform: uppercase;
	font-weight: 500;
	margin-bottom: 10px;
}

.WorkflowToolbarBlocksDropdown__list {
	display: flex;
	flex-direction: column;
	gap: 8px;
}
.WorkflowToolbarBlocksDropdown__list__item {
	display: grid;
	grid-template-columns: auto minmax(0, 1fr) auto;
	gap: 16px;
	align-items: center;
}
.WorkflowToolbarBlocksDropdown__list__item__description,
.WorkflowToolbarBlocksDropdown__list__item__title {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}
.WorkflowToolbarBlocksDropdown__list__item__description {
	font-weight: 400;
	color: var(--wdsColorGray4);
}
</style>
