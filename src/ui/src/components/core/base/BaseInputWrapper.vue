<template>
	<div
		ref="rootEl"
		class="BaseInputWrapper"
		:class="{ horizontal: isHorizontal }"
	>
		<label v-if="label">{{ label }}</label>
		<slot></slot>
	</div>
</template>

<script setup lang="ts">
defineProps({
	label: { type: String, required: false, default: undefined },
	isHorizontal: { type: Boolean, required: false },
});
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.BaseInputWrapper {
	display: flex;
	width: 100%;
	gap: 3px;
	flex-direction: column;
}

.horizontal {
	align-items: center;
	flex-direction: row-reverse;
	gap: 8px;
	justify-content: start;
}

label {
	font-size: 0.875rem;
	color: var(--primaryTextColor);
	margin-bottom: 4px;
	line-height: 150%;
}

.horizontal label {
	margin-bottom: 0px;
}
</style>
