<template>
	<div class="BuilderPanel">
		<div class="header">
			<div class="title">{{ name }}</div>
			<WdsButton
				variant="neutral"
				size="unpadded"
				@click="action.callback"
				v-for="action in actions"
				><i class="material-symbols-outlined">{{
					action.icon
				}}</i></WdsButton
			>
		</div>
		<div class="content"><slot></slot></div>
	</div>
</template>

<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";

export type BuilderPanelAction = {
	icon: string;
	callback: () => void;
};

const props = defineProps<{
	name: string;
	actions: BuilderPanelAction[];
}>();
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderPanel {
	border-top: 1px solid var(--builderSeparatorColor);
	display: flex;
	flex-direction: column;
	height: 100%;
	background: var(--builderBackgroundColor);
}

.BuilderPanel:not(:first-child) {
	border-left: 1px solid var(--builderSeparatorColor);
}

.header {
	min-height: 36px;
	flex: 0 0 36px;
	display: flex;
	align-items: center;
	padding: 8px 8px 8px 20px;
	border-bottom: 1px solid var(--builderSeparatorColor);
	gap: 12px;
}

.header .title {
	flex: 1 0 auto;
	font-size: 14px;
	font-style: normal;
	font-weight: 600;
	line-height: 140%;
}

.header .actions {
	display: flex;
	font-size: 16px;
}

.content {
	flex: 1 0 auto;
}
</style>
