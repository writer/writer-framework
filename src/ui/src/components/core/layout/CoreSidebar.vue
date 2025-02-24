<template>
	<div
		class="CoreSidebar"
		:style="rootStyle"
		:class="{
			collapsed: isCollapsed,
		}"
	>
		<div class="collapserContainer">
			<BaseCollapseButton v-model="isCollapsed" direction="left-right" />
		</div>
		<div class="container" data-writer-container>
			<slot></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { Component, FieldCategory, FieldType } from "@/writerTypes";
import {
	accentColor,
	primaryTextColor,
	secondaryTextColor,
	containerBackgroundColor,
	containerShadow,
	separatorColor,
	buttonColor,
	buttonTextColor,
	buttonShadow,
	cssClasses,
	startCollapsed,
} from "@/renderer/sharedStyleFields";
import BaseCollapseButton from "../base/BaseCollapseButton.vue";

const description =
	"A container component that organizes its children in a sidebar. Its parent must be a Page component.";

export default {
	writer: {
		name: "Sidebar",
		description,
		positionless: true,
		slot: "sidebar",
		allowedParentTypes: ["page"],
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			startCollapsed: {
				...startCollapsed,
				desc: undefined,
			},
			sidebarBackgroundColor: {
				name: "Background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
				default: "rgba(255, 255, 255, 0.3)",
			},
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { computed, inject, onMounted, Ref, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
const isCollapsed: Ref<boolean> = ref(fields.startCollapsed.value);
const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const selectedId = computed(() => ssbm?.firstSelectedId.value);

const rendererTop = ref(0);

const rootStyle = computed(() => {
	return {
		"max-height": `calc(100vh - ${rendererTop.value}px)`,
	};
});

watch(selectedId, (newSelectedId) => {
	if (!newSelectedId) return;
	if (!checkIfSidebarIsParent(newSelectedId)) return;
	isCollapsed.value = false;
});

const checkIfSidebarIsParent = (childId: Component["id"]): boolean => {
	const child = wf.getComponentById(childId);
	if (!child || child.type == "root") return false;
	if (child.parentId == componentId) return true;
	return checkIfSidebarIsParent(child.parentId);
};

onMounted(() => {
	const rendererEl: HTMLElement =
		document.querySelector(".ComponentRenderer");
	rendererTop.value =
		document.body.clientHeight - rendererEl?.parentElement.clientHeight;
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreSidebar {
	overflow: auto;
	padding: 16px;
	border-right: 1px solid var(--separatorColor);
	position: sticky;
	top: 0;
	background-color: var(--sidebarBackgroundColor);
}

.CoreSidebar:not(.collapsed) {
	width: 20vw;
	max-width: 300px;
}

.CoreSidebar.collapsed > .container {
	display: none;
}

.collapserContainer {
	display: flex;
	justify-content: right;
	margin-bottom: 16px;
}

@media only screen and (max-width: 768px) {
	.CoreSidebar {
		min-width: 100%;
		border-right: 0;
		border-bottom: 1px solid var(--separatorColor);
	}

	.CoreSidebar.collapsed > .collapserContainer {
		margin-bottom: 0;
	}
}
</style>
