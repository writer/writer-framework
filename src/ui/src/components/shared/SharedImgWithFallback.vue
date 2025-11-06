<template>
	<WdsSkeletonLoader v-if="isLoading" class="skeleton" :style="loaderStyle" />
	<img v-else :src="src" />
</template>

<script lang="ts" setup>
import {
	type CSSProperties,
	computed,
	type PropType,
	ref,
	toRef,
	watch,
} from "vue";
import { useAssetContentType } from "@/composables/useAssetContentType";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";

const props = defineProps({
	urls: { type: Array as PropType<string[]>, required: true },
	loaderMaxWidthPx: { type: Number, default: undefined },
	loaderMaxHeightPx: { type: Number, default: undefined },
});

const loaderStyle = computed(() => {
	const style: CSSProperties = {};
	if (props.loaderMaxWidthPx !== undefined) {
		style.maxWidth = `${props.loaderMaxWidthPx}px`;
		style.width = `${props.loaderMaxWidthPx}px`;
	}
	if (props.loaderMaxHeightPx !== undefined) {
		style.maxHeight = `${props.loaderMaxHeightPx}px`;
		style.height = `${props.loaderMaxHeightPx}px`;
	}
	return style;
});

const src = ref("");
const isLoading = ref(true);
const previousUrls = ref<string[]>([]);
let currentGeneration = 0;

const { fetchAssetContentType } = useAssetContentType();

// Helper function to check if arrays are deeply equal
function areUrlsEqual(a: string[], b: string[]): boolean {
	if (a.length !== b.length) return false;
	return a.every((url, index) => url === b[index]);
}

watch(
	toRef(props, "urls"),
	async (urls) => {
		// Skip if URLs haven't changed
		if (areUrlsEqual(urls, previousUrls.value)) {
			return;
		}

		previousUrls.value = [...urls];
		isLoading.value = true;
		src.value = "";
		const generation = ++currentGeneration;

		for (const url of urls) {
			if (generation !== currentGeneration) return;
			const contentType = await fetchAssetContentType(url);
			if (generation !== currentGeneration) return;
			// ensure that the content type is valid and not HTML (the server can responds with a default HTML page)
			if (!contentType || contentType === "text/html") continue;

			src.value = url;
			break;
		}
		if (generation !== currentGeneration) return;
		isLoading.value = false;
	},
	{ immediate: true },
);
</script>

<style scoped>
.skeleton {
	width: 100%;
	height: 100%;
	aspect-ratio: 1 / 1;
	border-radius: 4px;
}
</style>
