<template>
	<div class="BuilderPanel">
		<div class="header">
			<div class="title">Code</div>
			<WdsButton variant="neutral" size="unpadded"
				><i class="material-symbols-outlined">close</i></WdsButton
			>
			<WdsButton variant="neutral" size="unpadded"
				><i class="material-symbols-outlined">close</i></WdsButton
			>
		</div>
		<div class="content"><slot></slot></div>
	</div>
</template>

<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";
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

.header {
	min-height: 24px;
	flex: 0 0 24px;
	display: flex;
	align-items: center;
	padding: 8px 20px 8px 20px;
	border-bottom: 1px solid var(--builderSeparatorColor);
	gap: 12px;
}

.header .title {
	flex: 1 0 auto;
}

.header .actions {
	display: flex;
	font-size: 16px;
}

.content {
	flex: 1 0 auto;
}
</style>
