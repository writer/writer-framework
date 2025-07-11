<!-- eslint-disable vue/no-v-html -->

<template>
	<span :style="{ display: 'contents' }" v-html="rawHtml" />
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, useAttrs, watch } from "vue";
import { createIcons, icons } from "lucide";

defineOptions({
	inheritAttrs: false,
});

const props = defineProps({
	name: { type: String, required: true },
});

const attrs = useAttrs();

const rawHtml = ref("");

function renderIcon(name: string) {
	rawHtml.value = `<i data-lucide="${name}"></i>`;

	nextTick(() => {
		createIcons({
			icons,
			attrs: {
				width: "1em",
				height: "1em",
				...attrs,
			},
		});
	});
}

watch(
	() => props.name,
	(newName) => {
		renderIcon(newName);
	},
);

onMounted(() => {
	renderIcon(props.name);
});
</script>
