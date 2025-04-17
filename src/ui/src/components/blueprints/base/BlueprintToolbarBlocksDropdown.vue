<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import { Component } from "@/writerTypes";
import { computed, inject, PropType } from "vue";

const props = defineProps({
	components: { type: Array as PropType<Component[]>, required: true },
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

function isRunnable(component: Component) {
	if (component.type !== "blueprints_uieventtrigger") return true;

	const hasDefaultResult = Boolean(component.content.defaultResult);
	if (hasDefaultResult) return true;

	const fields = (component.outs ?? [])
		.map((o) => wf.getComponentById(o.toNodeId))
		.flatMap((c) => Object.values(c.content ?? {}));
	if (fields.length === 0) return true;

	const needResult = fields.some((field) => field.includes("@{result}"));

	return !needResult;
}

const options = computed(() =>
	props.components.map((block) => {
		const def = wf.getComponentDefinition(block.type);
		const title = block.content?.alias || getBlockType(block);
		const description = def?.name ?? block.type;

		return {
			id: block.id,
			disabled: !isRunnable(block),
			title,
			description: title === description ? undefined : description,
		};
	}),
);
</script>

<template>
	<div class="BlueprintToolbarBlocksDropdown">
		<p class="BlueprintToolbarBlocksDropdown__header">
			Start blueprint from
		</p>
		<div class="BlueprintToolbarBlocksDropdown__list">
			<div
				v-for="option of options"
				:key="option.id"
				class="BlueprintToolbarBlocksDropdown__list__item"
				:class="{
					'BlueprintToolbarBlocksDropdown__list__item--disabled':
						option.disabled,
				}"
			>
				<WdsButton
					variant="primary"
					size="smallIcon"
					custom-size="20px"
					:disabled="option.disabled"
					:data-writer-tooltip="
						option.disabled
							? 'Can not run without a default result. Go to this block to define a default result.'
							: 'Run the branch'
					"
					@click="$emit('runBranch', option.id)"
				>
					<i class="material-symbols-outlined">play_arrow</i>
				</WdsButton>
				<div>
					<p
						class="BlueprintToolbarBlocksDropdown__list__item__description"
					>
						{{ option.description }}
					</p>
					<p
						class="BlueprintToolbarBlocksDropdown__list__item__title"
					>
						{{ option.title }}
					</p>
				</div>
				<WdsButton
					variant="neutral"
					size="smallIcon"
					custom-size="20px"
					data-writer-tooltip="Jump to the blueprint"
					@click="$emit('jumpToComponent', option.id)"
				>
					<i class="material-symbols-outlined">jump_to_element</i>
				</WdsButton>
			</div>
		</div>
	</div>
</template>

<style lang="css" scoped>
.BlueprintToolbarBlocksDropdown {
	min-width: 185px;
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
	color: var(--wdsColorGray6);

	max-height: 300px;
	overflow-y: auto;
}
.BlueprintToolbarBlocksDropdown__header {
	font-size: 12px;
	text-transform: uppercase;
	font-weight: 500;
	margin-bottom: 10px;
}

.BlueprintToolbarBlocksDropdown__list {
	display: flex;
	flex-direction: column;
	gap: 8px;
}
.BlueprintToolbarBlocksDropdown__list__item {
	display: grid;
	grid-template-columns: auto minmax(0, 1fr) auto;
	gap: 16px;
	align-items: center;
}
.BlueprintToolbarBlocksDropdown__list__item__description,
.BlueprintToolbarBlocksDropdown__list__item__title {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}
.BlueprintToolbarBlocksDropdown__list__item__description {
	font-weight: 400;
	color: var(--wdsColorGray4);
}

.BlueprintToolbarBlocksDropdown__list__item--disabled
	.BlueprintToolbarBlocksDropdown__list__item__description,
.BlueprintToolbarBlocksDropdown__list__item--disabled
	.BlueprintToolbarBlocksDropdown__list__item__title {
	opacity: 50%;
}
</style>
