<template>
	<WdsButton
		size="smallIcon"
		variant="neutral"
		:loading="isCopying"
		class="floating-copy-button"
		:class="{ copied }"
		:label="copied ? 'Copied' : 'Copy'"
		data-writer-tooltip="Copy text"
		@click="copyToClipboard"
	>
		<i v-if="copied" class="material-symbols-outlined"> check_circle </i>
		<i v-else class="material-symbols-outlined"> content_copy </i>
	</WdsButton>
</template>

<script setup lang="ts">
import { useLogger } from "@/composables/useLogger";
import WdsButton from "@/wds/WdsButton.vue";
import { onBeforeUnmount, ref, toRef, watch } from "vue";

const props = defineProps({
	content: { type: String, required: true },
});

watch(toRef(props, "content"), () => (copied.value = false));

const isCopying = ref(false);
const copied = ref(false);
let timeout: ReturnType<typeof setTimeout> | undefined;

async function copyToClipboard() {
	if (timeout) {
		clearTimeout(timeout);
		timeout = undefined;
	}

	isCopying.value = true;

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
		isCopying.value = false;
	}
}

onBeforeUnmount(() => {
	if (timeout) clearTimeout(timeout);
});
</script>

<style scoped>
.floating-copy-button {
	position: absolute;
	top: 0;
	right: 8px;
	z-index: 10;
	border-radius: 6px;
	transition: all 0.2s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 16px;
	width: 16px;
}

.floating-copy-button:hover {
	color: var(--wdsColorBlue4);
}

/* Animation for copied state */
.floating-copy-button.copied {
	color: var(--wdsColorGreen5);
}
</style>
