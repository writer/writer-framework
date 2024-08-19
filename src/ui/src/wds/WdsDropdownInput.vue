<template>
	<select v-model="model">
		<slot></slot>
	</select>
</template>

<script setup lang="ts">
const model = defineModel<string>();
</script>

<style scoped>
select {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.25px;
	font-size: 0.875rem;
	max-width: 100%;
	width: fit-content;
	outline: none;
	cursor: pointer;
}

select:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
