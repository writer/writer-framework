<template>
	<img :src="src" />
</template>

<script lang="ts" setup>
import { useAssetContentType } from "@/composables/useAssetContentType";
import { PropType, ref, toRef, watch } from "vue";

const props = defineProps({
	urls: { type: Array as PropType<string[]>, required: true },
});

const src = ref("");

const { fetchAssetContentType } = useAssetContentType();

watch(
	toRef(props, "urls"),
	async (urls) => {
		src.value = "";

		for (const url of urls) {
			const contentType = await fetchAssetContentType(url);
			// ensure that the content type is valid and not HTML (the server can responds with a default HTML page)
			if (!contentType || contentType === "text/html") continue;
			return (src.value = url);
		}
	},
	{ immediate: true },
);
</script>
