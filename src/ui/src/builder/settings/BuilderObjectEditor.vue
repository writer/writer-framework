<script setup lang="ts">
import { PropType } from "vue";

type Mode = "assisted" | "freehand";
defineProps({
	mode: { type: String as PropType<Mode>, required: true },
});

defineModel({
	type: Object as PropType<Record<string, string | number | boolean>>,
});
</script>

<template>
	<WdsTabs
		class="BuilderFieldsOptions__tabs"
		:tabs="tabs"
		:model-value="mode"
		@update:model-value="setMode"
	/>
</template>
