<template>
	<div v-show="isVisible" class="CoreTab">
		<button
			v-if="isTabBit"
			class="bit"
			:class="{ active: isTabActive }"
			tabindex="0"
			@click="activateTab"
		>
			{{ fields.name.value }}
		</button>
		<BaseContainer
			v-if="isContentDisplaying"
			v-show="isTabActive"
			class="container"
			:content-h-align="fields.contentHAlign.value"
			:content-padding="fields.contentPadding.value"
		>
			<slot></slot>
		</BaseContainer>
	</div>
</template>

<script lang="ts">
/**
 * This component renders differently depending on the instance number of
 * the direct child of the relevant Tab Container.
 *
 * In standard usage, the Tab will be a direct child of the Tab Container.
 * Hence, the Tab instance number is used.
 * However, if using a Repeater with a Tab inside, the instance number of the
 * Repeater is used for this purpose.
 *
 * 0 = This component renders the tab bit of the Tab component.
 * 1 = This component renders the content portion of the Tab component.
 */

const TAB_BIT_INSTANCE_NUMBER = 0;
const CONTENT_DISPLAYING_INSTANCE_NUMBER = 1;

import { Component, FieldType, InstancePath } from "@/writerTypes";
import { useEvaluator } from "@/renderer/useEvaluator";
import {
	contentHAlign,
	cssClasses,
	contentPadding,
} from "@/renderer/sharedStyleFields";

const description =
	"A container component that displays its child components as a tab inside a Tab Container.";

export default {
	writer: {
		name: "Tab",
		description,
		allowedParentTypes: ["tabs", "repeater"],
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			name: {
				name: "Name",
				default: "(No name)",
				init: "Tab Name",
				type: FieldType.Text,
			},
			contentPadding: {
				...contentPadding,
				default: "16px",
			},
			contentHAlign,
			cssClasses,
		},
		previewField: "name",
	},
};
</script>
<script setup lang="ts">
import { computed, inject, onBeforeMount, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import BaseContainer from "../base/BaseContainer.vue";

const fields = inject(injectionKeys.evaluatedFields);
const instancePath = inject(injectionKeys.instancePath);
const instanceData = inject(injectionKeys.instanceData);
const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const { isComponentVisible } = useEvaluator(wf);
const selectedId = computed(() => ssbm?.firstSelectedId.value);

const getDirectChildInstanceNegativeIndex = () => {
	for (let i = -2; i > -1 * instancePath.length; i--) {
		const item = instancePath.at(i);
		const { type } = wf.getComponentById(item.componentId);
		if (type !== "tabs") continue;
		return i + 1;
	}
	return;
};

const tabContainerDirectChildInstanceItem = computed(() => {
	const i = getDirectChildInstanceNegativeIndex();
	return instancePath.at(i);
});

const instanceNumber = computed<number | undefined>(
	() => tabContainerDirectChildInstanceItem?.value.instanceNumber,
);

const isTabBit = computed(
	() => instanceNumber.value === TAB_BIT_INSTANCE_NUMBER,
);
const isContentDisplaying = computed(
	() => instanceNumber.value === CONTENT_DISPLAYING_INSTANCE_NUMBER,
);

const isVisible = computed(() => {
	if (!isComponentVisible(componentId)) return false;
	return isTabBit.value || (isContentDisplaying.value && isTabActive.value);
});

const getTabContainerData = () => {
	for (let i = -1; i > -1 * instancePath.length; i--) {
		const item = instancePath.at(i);
		const { type } = wf.getComponentById(item.componentId);
		if (type !== "tabs") continue;
		return instanceData.at(i);
	}
	return;
};

const getMatchingTabInstancePath = () => {
	const i = getDirectChildInstanceNegativeIndex();
	const itemsBefore = instancePath.slice(0, i);
	const itemsAfter = i + 1 < 0 ? instancePath.slice(i + 1) : [];
	const matchingInstancePath = [
		...itemsBefore,
		{
			componentId: instancePath.at(i).componentId,
			instanceNumber: CONTENT_DISPLAYING_INSTANCE_NUMBER,
		},
		...itemsAfter,
	];
	return matchingInstancePath;
};

const activateTab = () => {
	const tabContainerData = getTabContainerData();
	tabContainerData.value = {
		activeTab: getMatchingTabInstancePath(),
	};
};

const checkIfTabIsParent = (childId: Component["id"]): boolean => {
	const child = wf.getComponentById(childId);
	if (!child || child.type == "root") return false;
	if (child.parentId == componentId) return true;
	return checkIfTabIsParent(child.parentId);
};

watch(selectedId, (newSelectedId) => {
	if (!newSelectedId) return;
	if (!checkIfTabIsParent(newSelectedId)) return;
	activateTab();
});

const isTabActive = computed(() => {
	let contentDisplayingInstancePath: InstancePath;
	if (isTabBit.value) {
		contentDisplayingInstancePath = getMatchingTabInstancePath();
	} else {
		contentDisplayingInstancePath = instancePath;
	}
	const tabContainerData = getTabContainerData();
	const activeTab = tabContainerData.value?.activeTab;
	return (
		JSON.stringify(activeTab) ==
		JSON.stringify(contentDisplayingInstancePath)
	);
});

onBeforeMount(() => {
	if (isTabBit.value) return;
	const tabContainerData = getTabContainerData();
	const activeTab = tabContainerData.value?.activeTab;
	if (activeTab) return;
	if (!isComponentVisible(componentId, instancePath)) return;
	tabContainerData.value = { activeTab: instancePath };
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

button.bit {
	padding: 11.5px 0 9.5px 0;
	border: none;
	margin: 0;
	background: unset;
	color: var(--secondaryTextColor);
	font-size: 0.875rem;
	border-bottom: 2px solid transparent;
	outline: none;
	cursor: pointer;
}

button.bit:hover {
	padding: 11.5px 0 9.5px 0;
	border: none;
	margin: 0;
	background: unset;
	color: var(--secondaryTextColor);
	font-size: 0.875rem;
	border-bottom: 2px solid var(--separatorColor);
	outline: none;
}

button.bit:focus {
	color: var(--primaryTextColor);
}

button.bit.active {
	font-weight: 500;
	color: var(--primaryTextColor);
	border-bottom: 2px solid var(--primaryTextColor);
}
</style>
