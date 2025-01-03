<template>
	<div
		class="WorkflowsNodeNamer"
		:class="{
			beingEdited: isAliasBeingEdited,
			hasEyebrow: isAliased || isAliasBeingEdited,
		}"
		data-writer-unselectable="true"
	>
		<div
			v-if="isGroupNode && !(isAliased || isAliasBeingEdited)"
			class="groupName"
		>
			<div class="eyebrow">{{ groupType }}</div>
		</div>
		<div class="blockName" @click="enableEditor">
			{{ blockName }}
		</div>
		<div class="alias">
			<div
				v-if="isAliased || isAliasBeingEdited"
				ref="aliasEditorEl"
				class="aliasEditor"
				:contenteditable="isAliasBeingEdited"
				data-writer-unselectable="true"
				@click="enableEditor"
				@mousemove="handleAliasEditorMousemove"
				@blur="handleAliasChange"
				@keydown.enter="handleAliasChange"
			>
				{{ aliasFieldValue }}
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, nextTick, ref, useTemplateRef } from "vue";
import { useComponentActions } from "@/builder/useComponentActions";
import { Component } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";

const props = defineProps<{
	componentId: Component["id"];
}>();

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const aliasFieldValue = computed(
	() => wf.getComponentById(props.componentId)?.content["alias"],
);

const blockName = computed(() => {
	const def = wf.getComponentDefinitionById(props.componentId);
	if (
		(isAliased.value || isAliasBeingEdited.value) &&
		groupType.value != def.name
	) {
		return `${groupType.value} - ${def.name}`;
	} else if (groupType.value == def.name) {
		return "...";
	} else {
		return def.name;
	}
});

const isAliased = computed(() => Boolean(aliasFieldValue.value));
const aliasEditorEl = useTemplateRef("aliasEditorEl");
const isAliasBeingEdited = ref(false);

async function enableEditor() {
	if (isAliasBeingEdited.value) return;

	isAliasBeingEdited.value = true;
	await nextTick();

	const el = aliasEditorEl.value;
	el.focus();
	const range = document.createRange();
	const selection = window.getSelection();
	range.setStart(el, el.childNodes.length);
	range.collapse(true);
	selection.removeAllRanges();
	selection.addRange(range);
}

function handleAliasChange() {
	const newValue = aliasEditorEl.value.textContent;
	aliasEditorEl.value.blur();
	isAliasBeingEdited.value = false;
	setContentValue(props.componentId, "alias", newValue);
}

function handleAliasEditorMousemove(ev: MouseEvent) {
	if (!isAliasBeingEdited.value) return;
	ev.stopPropagation();
}

const groupType = computed(() => {
	const def = wf.getComponentDefinitionById(props.componentId);
	const groupType = wf.getGroupType(def.type);
	return wf.getComponentDefinition(groupType).name;
});

const isGroupNode = computed(() => {
	const def = wf.getComponentDefinitionById(props.componentId);
	return wf.isGroupNode(def.type);
});
</script>

<style scoped>
.WorkflowsNodeNamer {
	width: 100%;
	overflow: hidden;
}

.blockName {
	transition: 0.2s ease-in-out;
	transition-property: color, font-size;
}

.groupName {
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
	background: var(--builderBackgroundColor) !important;
}

.WorkflowsNodeNamer.hasEyebrow .blockName {
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
	background: var(--builderBackgroundColor) !important;
}

.WorkflowsNodeNamer:not(.hasEyebrow) .blockName {
	cursor: text;
	font-size: 14px;
	font-style: normal;
	font-weight: 500;
	line-height: 140%;
	padding: 4px;
	margin-left: -4px;
	border-radius: 4px;
}

.alias {
	transition: 0.2s ease-in-out;
	transition-property: top;
	position: relative;
}

.WorkflowsNodeNamer:not(.hasEyebrow) .alias {
	top: -24px;
}

.WorkflowsNodeNamer.hasEyebrow .alias {
	top: 0;
}

.aliasEditor {
	transition-property: color, font-size;
	padding: 2px 4px 2px 4px;
	margin-bottom: -2px;
	margin-left: -4px;
	border-radius: 4px;
	width: 100%;
	outline: none;
	border: none;
	font-size: 14px;
	font-style: normal;
	font-weight: 500;
	line-height: 140%;
	cursor: text;
}

.WorkflowsNodeNamer.beingEdited .aliasEditor {
	background: var(--builderSubtleSeparatorColor);
}
</style>
