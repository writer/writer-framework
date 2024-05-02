<template>
	<div ref="rootEl" class="BaseInputWrapper">
		<label>{{ props.label }}</label>
		<slot></slot>
	</div>
</template>

<script setup lang="ts">
const props = defineProps<{
	label: string;
}>();
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.BaseInputWrapper {
	display: flex;
	width: 100%;
	gap: 3px;
	flex-direction: column;
	font-size: 0.875rem;
}

label {
	color: var(--primaryTextColor);
	margin-bottom: 4px;
	line-height: 150%;
}
</style>
