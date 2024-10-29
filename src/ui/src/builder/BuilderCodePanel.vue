<template>
	<BuilderPanel class="BuilderCodePanel"> code kokokoko </BuilderPanel>
</template>

<script setup lang="ts">
import BuilderPanel from "./BuilderPanel.vue";
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderCodePanel {
	border-top: 1px solid var(--builderSeparatorColor);
	display: flex;
	flex-direction: column;
	height: 100%;
}
</style>
