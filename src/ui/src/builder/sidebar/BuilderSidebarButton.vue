<script setup lang="ts">
defineProps({
	icon: { type: String, required: true },
	active: { type: Boolean },
	disabled: { type: Boolean },
});
</script>

<template>
	<button
		class="BuilderSidebarButton"
		:class="{ 'BuilderSidebarButton--active': active }"
		role="button"
		:disabled="disabled"
	>
		<span class="material-symbols-outlined">{{ icon }}</span>
	</button>
</template>

<style lang="css" scoped>
.BuilderSidebarButton {
	border-radius: 8px;
	background-color: transparent;
	color: white;
	border: none;

	height: 32px;
	width: 32px;

	font-size: 16px;

	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
}
.BuilderSidebarButton[disabled] {
	opacity: 50%;
	cursor: not-allowed;
}
.BuilderSidebarButton:hover {
	background: var(--wdsColorGray5);
}

.BuilderSidebarButton--active {
	background: var(--wdsColorGray6);
}
</style>
