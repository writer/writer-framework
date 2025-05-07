<template>
	<button
		class="WdsTab"
		:class="{ 'WdsTab--disabled': disabled, 'WdsTab--selected': selected }"
		type="button"
		:disabled="Boolean(disabled)"
		:data-writer-tooltip="tooltip"
		@click="$emit('click')"
	>
		<slot />
	</button>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps({
	disabled: { type: [Boolean, String], default: undefined },
	selected: { type: Boolean },
});

const tooltip = computed(() =>
	typeof props.disabled === "string" ? props.disabled : undefined,
);

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
	cursor: not-allowed;
}

.WdsTab--selected {
	background-color: var(--wdsColorBlue2);
}
</style>
