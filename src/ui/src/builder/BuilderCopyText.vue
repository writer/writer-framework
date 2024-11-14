<template>
	<span
		class="BuilderCopyText"
		:data-writer-tooltip="tooltipText"
		@click="copyText"
	>
		<slot></slot>
	</span>
</template>

<script setup lang="ts">
import { ref } from "vue";
const tooltipText = ref("Copy to clipboard");

function copyText(ev: MouseEvent) {
	const copyText = (ev.target as HTMLElement).textContent;
	navigator.clipboard.writeText(copyText);
	tooltipText.value = "Copied!";
	setTimeout(() => {
		tooltipText.value = "Copy to clipboard";
	}, 1000);
}
</script>

<style scoped>
.BuilderCopyText {
	cursor: pointer;
}
</style>
