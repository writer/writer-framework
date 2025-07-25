<template>
	<div
		class="WdsTabs"
		:class="{
			'WdsTabs--variant-bar': variant === 'bar',
			'WdsTabs--variant-chip': variant === 'chip',
		}"
	>
		<WdsTab
			v-for="tab of tabs"
			:key="tab.value"
			:variant
			:disabled="tab.disabled"
			:selected="tab.value === selected"
			@click="selected = tab.value"
			>{{ tab.label }}</WdsTab
		>
	</div>
</template>

<script lang="ts">
export interface WdsTabOptions<Value extends string = string> {
	label: string;
	value: Value;
	disabled?: boolean | string;
}
</script>

<script setup lang="ts">
import { PropType } from "vue";
import WdsTab, { type WdsTabVariant } from "./WdsTab.vue";

defineProps({
	tabs: {
		type: Array as PropType<WdsTabOptions[] | Readonly<WdsTabOptions[]>>,
		required: true,
	},
	variant: {
		type: String as PropType<WdsTabVariant>,
		default: "chip",
	},
});

const selected = defineModel({ type: String });
</script>

<style scoped>
.WdsTabs {
	display: flex;
}

.WdsTabs--variant-bar {
	gap: 32px;
	overflow-x: auto;
	border-bottom: 1px solid var(--wdsColorGray2);
}

.WdsTabs--variant-chip {
	gap: 16px;
	flex-wrap: wrap;
}
</style>
