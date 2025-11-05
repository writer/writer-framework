<template>
	<WdsSkeletonLoader v-if="isLoading" class="skeleton" />
	<img v-else :src="src" />
</template>

<script lang="ts" setup>
import { type PropType, ref, toRef, watch } from "vue";
import { useAssetContentType } from "@/composables/useAssetContentType";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";

const props = defineProps({
	urls: { type: Array as PropType<string[]>, required: true },
});

const src = ref("");
const isLoading = ref(true);
const previousUrls = ref<string[]>([]);

const { fetchAssetContentType } = useAssetContentType();

// Helper function to check if arrays are deeply equal (like React.memo)
function areUrlsEqual(a: string[], b: string[]): boolean {
	if (a.length !== b.length) return false;
	return a.every((url, index) => url === b[index]);
}

watch(
	toRef(props, "urls"),
	async (urls) => {
		// Skip if URLs haven't changed (React.memo behavior)
		if (areUrlsEqual(urls, previousUrls.value)) {
			return;
		}

		previousUrls.value = [...urls];
		isLoading.value = true;
		src.value = "";

		for (const url of urls) {
			const contentType = await fetchAssetContentType(url);
			// ensure that the content type is valid and not HTML (the server can responds with a default HTML page)
			if (!contentType || contentType === "text/html") continue;

			src.value = url;
			break;
		}

		isLoading.value = false;
	},
	{ immediate: true },
);
</script>

<style scoped>
.skeleton {
	width: 100%;
	height: 100%;
}
</style>
