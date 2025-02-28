<template>
	<WdsProgressLinear
		class="BuilderCodePanelFileUploading"
		:progress="progress"
		:size-px="12"
		:stroke-width="2"
	/>
</template>

<script setup lang="ts">
import WdsProgressLinear from "@/wds/WdsProgressLinear.vue";
import { ref, onMounted } from "vue";

const props = defineProps({
	timeMs: { type: Number, required: true },
});

const progress = ref(0);

onMounted(() => {
	let startTime: number;
	const updateProgress = (timestamp: number) => {
		if (!startTime) startTime = timestamp;
		const elapsed = timestamp - startTime;
		progress.value = Math.min((elapsed / props.timeMs) * 100, 100);

		if (progress.value < 100) {
			requestAnimationFrame(updateProgress);
		}
	};
	requestAnimationFrame(updateProgress);
});
</script>

<style lang="css" scoped>
.BuilderCodePanelFileUploading {
	min-width: 12px;
}
</style>
