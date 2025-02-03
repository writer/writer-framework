<template>
	<BaseMarkdownRaw
		v-if="isMarkedLoaded"
		:raw-markdown="String(marked.parse(props.rawText)).trim()"
		class="BaseMarkdown"
	></BaseMarkdownRaw>
</template>

<script setup lang="ts">
import { onBeforeMount, ref } from "vue";
import BaseMarkdownRaw from "./BaseMarkdownRaw.vue";

let marked: typeof import("marked");
const isMarkedLoaded = ref(false);

const props = defineProps<{
	rawText: string;
}>();

onBeforeMount(async () => {
	marked = await import("marked");
	isMarkedLoaded.value = true;
});
</script>
