<template>
	<WdsButton
		size="small"
		variant="tertiary"
		:loading="isCoping"
		@click="copyToClipboard"
	>
		<span v-if="copied" class="material-symbols-outlined">
			check_circle
		</span>
		{{ copied ? "Copied to clipboard" : label }}</WdsButton
	>
</template>

<script setup lang="ts">
import { useLogger } from "@/composables/useLogger";
import WdsButton from "@/wds/WdsButton.vue";
import { onBeforeUnmount, ref, toRef, watch } from "vue";

const props = defineProps({
	label: { type: String, required: true },
	content: { type: String, required: true },
});

watch(toRef(props, "content"), () => (copied.value = false));

const isCoping = ref(false);
const copied = ref(false);
let timeout: ReturnType<typeof setTimeout> | undefined;

async function copyToClipboard() {
	if (timeout) {
		clearTimeout(timeout);
		timeout = undefined;
	}

	isCoping.value = true;

	try {
		await navigator.clipboard.writeText(props.content);
		copied.value = true;
		timeout = setTimeout(() => {
			copied.value = false;
			timeout = undefined;
		}, 3_000);
	} catch (error) {
		useLogger().error(error);
	} finally {
		isCoping.value = false;
	}
}

onBeforeUnmount(() => {
	if (timeout) clearTimeout(timeout);
});
</script>
