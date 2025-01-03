<template>
	<button
		class="WdsTab"
		:class="{ 'WdsTab--disabled': disabled, 'WdsTab--selected': selected }"
		type="button"
		@click="$emit('click')"
	>
		<slot />
	</button>
</template>

<script setup lang="ts">
defineProps({
	disabled: { type: Boolean },
	selected: { type: Boolean },
});

defineEmits({
	click: () => true,
});
</script>

<style scoped>
.WdsTab {
	/* reset button */
	border: none;
	background-color: transparent;
	cursor: pointer;

	padding: 4px 20px 4px 20px;
	gap: 10px;
	border-radius: 8px;
}

.WdsTab:hover {
	background-color: var(--wdsColorBlue1);
}

.WdsTab--disabled {
	color: var(--wdsColorGray4);
}

.WdsTab--selected {
	background-color: var(--wdsColorBlue2);
}
</style>
