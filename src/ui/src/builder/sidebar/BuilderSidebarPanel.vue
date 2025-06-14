<template>
	<div class="BuilderSidebarPanel">
		<div v-if="!hideSearchBar" class="BuilderSidebarPanel__inputContainer">
			<WdsTextInput
				v-model="model"
				class="searchInput"
				left-icon="search"
				data-automation-action="search"
				:placeholder="placeholder"
				:right-text="searchRightText"
				right-icon="close"
				@right-icon-click="model = ''"
			/>
		</div>
		<div class="BuilderSidebarPanel__main"><slot></slot></div>
		<div class="BuilderSidebarPanel__footer">
			<slot name="footer"></slot>
		</div>
	</div>
</template>

<script setup lang="ts">
import WdsTextInput from "@/wds/WdsTextInput.vue";
import { computed } from "vue";

const model = defineModel({ type: String, required: false, default: "" });

const props = defineProps({
	hideSearchBar: { type: Boolean, required: false },
	placeholder: { type: String, required: false, default: "" },
	searchCount: { type: Number, required: false, default: undefined },
});

const searchRightText = computed(() => {
	if (props.searchCount === undefined) return undefined;

	return `${props.searchCount} result${props.searchCount === 1 ? "" : "s"}`;
});
</script>

<style scoped>
.BuilderSidebarPanel {
	display: grid;
	grid-template-rows: 1fr;
	grid-template-columns: 100%;
	height: 100%;
	width: 100%;
	position: relative;
	overflow-x: auto;
	overflow-y: auto;
}

.BuilderSidebarPanel:has(.BuilderSidebarPanel__inputContainer) {
	grid-template-rows: auto 1fr;
}

.BuilderSidebarPanel__inputContainer {
	position: sticky;
	top: 0;
	left: 0;
	right: 0;
	padding: 16px 16px 0 16px;
	margin-bottom: 16px;
	background: var(--builderBackgroundColor);
	z-index: 2;
}

.searchInput {
	background: var(--builderSubtleSeparatorColor);
	width: 100%;
}

.BuilderSidebarPanel__main {
	display: flex;
	padding-left: 16px;
	padding-right: 16px;
	gap: 16px;
	flex-direction: column;
}
.BuilderSidebarPanel__footer {
	position: sticky;
	bottom: 0px;
	left: 0px;
}

.categories {
	display: flex;
}

.category .header {
	font-size: 12px;
	font-weight: 500;
	line-height: 12px; /* 100% */
	letter-spacing: 1.3px;
	text-transform: uppercase;
	color: var(--builderSecondaryTextColor);
	margin-bottom: 16px;
}

.tools {
	display: grid;
	grid-template-columns: 24px 1fr;
	grid-template-rows: auto;
	padding: 0 8px 0 8px;
	row-gap: 12px;
	column-gap: 4px;
}
</style>
