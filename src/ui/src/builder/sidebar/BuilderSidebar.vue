<template>
	<div class="BuilderSidebar">
		<BuilderSidebarToolkit></BuilderSidebarToolkit>
		<BuilderSidebarComponentTree></BuilderSidebarComponentTree>
	</div>
</template>

<script setup lang="ts">
// import BuilderSidebarToolbar from "./BuilderSidebarToolbar.vue";
import BuilderSidebarToolkit from "./BuilderSidebarToolkit.vue";
import BuilderSidebarComponentTree from "./BuilderSidebarComponentTree.vue";
</script>

<style scoped>
.BuilderSidebar {
	display: flex;
	flex-direction: column;
	height: 100%;
}

.BuilderSidebar > *:not(:first-child) {
	border-top: 1px solid var(--builderSeparatorColor);
}

.BuilderSidebar > * {
	flex: 0 0 50%;
	overflow-x: hidden;
	overflow-y: auto;
}
</style>
