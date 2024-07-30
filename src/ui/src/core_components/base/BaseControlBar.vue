<template>
	<div class="BaseControlBar">
		<button v-if="props.copyStructuredContent" class="control-button"
			@click="copyToClipboard({ text: props.copyStructuredContent })">
			Copy JSON
		</button>
		<button v-if="props.copyRawContent" class="control-button"
			@click="copyToClipboard({ text: props.copyRawContent })">
			Copy
		</button>
	</div>
</template>

<script setup lang="ts">
const props = defineProps<{
	copyRawContent?: string;
	copyStructuredContent?: string;
}>();

function setClipboardData<T = unknown>(
	source: T & { clipboardData: DataTransfer | null | undefined },
	{ text, html }: { text?: string; html?: string },
): void {
	if (text) {
		source.clipboardData?.setData("text/plain", text);
		source.clipboardData?.setData("Text", text); // IE mimetype
	}

	if (html) {
		source.clipboardData?.setData("text/html", html);
	}
}

function copyToClipboard({
	text = "",
}: {
	text?: string;
}) {
	try {
		navigator.clipboard.writeText(text);
	} catch (error) {
		console.error(error.message);
	}
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.BaseControlBar {
	margin: 10px 0;
	display: flex;
	flex-direction: row;
	justify-content: flex-end;
}

.control-button {
	background-color: var(--buttonColor);
	border: none;
	border-radius: 8px;
	color: white;
	cursor: pointer;
	font-size: 11px;
	margin-right: 10px;
	padding: 4px 8px;

	&:hover {
		opacity: 0.9;
	}
}
</style>
