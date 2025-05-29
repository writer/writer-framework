<script setup lang="ts">
defineProps({
	icon: { type: String, required: true },
	active: { type: Boolean },
	disabled: { type: Boolean },
	href: { type: String, required: false, default: undefined },
});
</script>

<template>
	<a v-if="href" class="BuilderSidebarButton" :href="href">
		<span class="material-symbols-outlined">{{ icon }}</span>
	</a>
	<button
		v-else
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
	text-decoration: none;
}
.BuilderSidebarButton:focus-visible {
	outline: 2px solid var(--wdsColorBlue5);
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
