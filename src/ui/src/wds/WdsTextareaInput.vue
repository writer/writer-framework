<template>
	<textarea v-model="model"></textarea>
</template>

<script setup lang="ts">
const model = defineModel<string>();
</script>

<style scoped>
textarea {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
	color: var(--primaryTextColor);
}

textarea:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
