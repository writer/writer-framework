<template>
	<div class="WdsTabs">
		<WdsTab
			v-for="tab of tabs"
			:key="tab.value"
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
	disabled?: boolean;
}
</script>

<script setup lang="ts">
import { PropType } from "vue";
import WdsTab from "./WdsTab.vue";

defineProps({
	tabs: {
		type: Array as PropType<WdsTabOptions[] | Readonly<WdsTabOptions[]>>,
		required: true,
	},
});

const selected = defineModel({ type: String });
</script>

<style scoped>
.WdsTabs {
	display: flex;
	gap: 16px;
	flex-wrap: wrap;
}
</style>
