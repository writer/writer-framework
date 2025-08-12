<template>
	<CustomIcon v-if="isCustomIconName(name)" :name="name" />
	<LucideIcon v-else :name="name" />
</template>

<script setup lang="ts">
import CustomIcon, { isCustomIconName } from "./WdsIcons/CustomIcon.vue";
import LucideIcon from "./WdsIcons/LucideIcon.vue";

defineOptions({
	inheritAttrs: false,
});

defineProps({
	name: { type: String, required: true },
});
</script>
