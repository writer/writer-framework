<!-- eslint-disable vue/no-v-html -->

<template>
	<span :style="{ display: 'contents' }" v-html="rawHtml" />
</template>

<script setup lang="ts">
import { nextTick, ref, toRef, watch } from "vue";
import { createIcons, icons } from "lucide";

defineOptions({
	inheritAttrs: false,
});

const props = defineProps({
	name: { type: String, required: true },
});

const rawHtml = ref("");

function renderIcon(name: string) {
	rawHtml.value = `<i data-lucide="${name}"></i>`;

	nextTick(() => {
		createIcons({
			icons,
			attrs: {
				width: "1em",
				height: "1em",
			},
		});
	});
}

watch(
	toRef(props, "name"),
	(newName) => {
		renderIcon(newName);
	},
	{
		immediate: true,
		flush: "post",
	},
);
</script>
