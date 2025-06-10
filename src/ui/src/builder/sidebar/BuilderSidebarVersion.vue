<script setup lang="ts">
defineProps({
	version: { type: String, required: true },
});
</script>

<template>
	<span class="BuilderSidebarVersion">
		<span class="BuilderSidebarVersion__capsule"> BETA {{ version }} </span>
	</span>
</template>

<style lang="css" scoped>
.BuilderSidebarVersion {
	background-color: transparent;
	color: var(--wdsColorWhite);
	margin: 0 auto;
	height: 64px;
	width: 32px;
	display: flex;
	align-items: center;
	justify-content: center;
}
.BuilderSidebarVersion__capsule {
	background: var(--wdsColorGray6);
	white-space: nowrap;
	font-size: 13px;
	font-family: Poppins, sans-serif;
	transform: rotate(-90deg);
	border-radius: 4px;
	padding: 1px 8px;
	gap: 8px;
}
</style>
