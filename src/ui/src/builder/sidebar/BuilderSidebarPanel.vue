<template>
	<div class="BuilderSidebarPanel">
		<div class="inputContainer">
			<WdsTextInput
				v-model="model"
				class="searchInput"
				left-icon="search"
				data-automation-action="search"
				:placeholder="placeholder"
			></WdsTextInput>
		</div>
		<div class="main"><slot></slot></div>
	</div>
</template>

<script setup lang="ts">
import WdsTextInput from "@/wds/WdsTextInput.vue";

const model = defineModel<string>();

defineProps<{
	placeholder: string;
}>();
</script>

<style scoped>
.BuilderSidebarPanel {
	display: flex;
	flex-direction: column;
	height: 100%;
	position: relative;
	overflow-x: hidden;
	overflow-y: scroll;
}

.inputContainer {
	position: sticky;
	top: 0;
	padding: 16px 16px 0 16px;
	background: var(--builderBackgroundColor);
	z-index: 2;
}

.searchInput {
	background: var(--builderSubtleSeparatorColor);
}

.main {
	display: flex;
	flex: 1 0 auto;
	padding: 16px;
	gap: 16px;
	flex-direction: column;
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
