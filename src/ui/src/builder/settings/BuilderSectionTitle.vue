<template>
	<div class="BuilderSectionTitle">
		<i class="material-symbols-outlined">{{ icon }}</i>
		<h3>{{ label }}</h3>
	</div>
</template>

<script setup lang="ts">
defineProps({
	icon: { type: String, required: true },
	label: { type: String, required: true },
});
</script>

<style lang="css" scoped>
@import "../sharedStyles.css";
.BuilderSectionTitle {
	display: flex;
	gap: 8px;
	align-items: center;
	font-size: 1rem;
}
</style>
