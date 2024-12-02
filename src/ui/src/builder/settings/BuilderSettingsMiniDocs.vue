<template>
	<div
		v-dompurify-html="miniDocsHtml"
		class="BuilderSettingsMiniDocs markdown"
	>
		{{ miniDocsHtml }}
	</div>
</template>

<script setup lang="ts">
import { marked } from "marked";

const props = defineProps<{
	rawMiniDocs: string;
}>();

const miniDocsHtml = marked.parse(props.rawMiniDocs);
</script>

<style scoped>
@import "../sharedStyles.css";

/*
Markdown styling
*/

.markdown:deep() pre {
	background-color: var(--builderSubtleSeparatorColor);
	font-family: monospace;
	padding: 8px;
	border-radius: 4px;
}

.markdown:deep() code {
	background-color: var(--builderSubtleSeparatorColor);
	font-family: monospace;
	padding: 2px;
}

.markdown:deep() pre > code {
	background-color: unset;
}
</style>
