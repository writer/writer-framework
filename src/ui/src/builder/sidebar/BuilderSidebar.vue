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
	display: grid;
	grid-template-rows: 1fr 1fr;
	height: 100%;
}

.BuilderSidebar > *:not(:first-child) {
	border-top: 1px solid var(--builderSeparatorColor);
}
</style>
