<template>
	<div class="SharedControlBar">
		<SharedButtonCopyClipboard
			v-if="props.copyStructuredContent"
			label="Copy JSON"
			:content="props.copyStructuredContent"
		/>
		<SharedButtonCopyClipboard
			v-if="props.copyRawContent"
			label="Copy"
			:content="props.copyRawContent"
		/>
	</div>
</template>

<script setup lang="ts">
import SharedButtonCopyClipboard from "./SharedButtonCopyClipboard.vue";

const props = defineProps({
	copyRawContent: { type: String, required: false, default: undefined },
	copyStructuredContent: {
		type: String,
		required: false,
		default: undefined,
	},
});
</script>

<style scoped>
.SharedControlBar {
	margin-top: 8px;
	display: flex;
	flex-direction: row;
	justify-content: flex-end;
	gap: 8px;
}
</style>
