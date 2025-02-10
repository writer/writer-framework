<template>
	<div v-dompurify-html="rawMarkdown" class="markdown"></div>
</template>

<script setup lang="ts">
defineProps({
	rawMarkdown: { type: String, required: true },
});
</script>

<style scoped>
.markdown {
	font-size: 0.875rem;
}

.markdown:deep() h1,
.markdown:deep() h2,
.markdown:deep() h3,
.markdown:deep() h4 {
	margin: 0;
	color: var(--primaryTextColor);
}

.markdown:deep() h1 {
	font-size: 1.5rem;
	letter-spacing: 0.1875rem;
	font-weight: 600;
	line-height: 162.5%;
}

.markdown:deep() h2 {
	font-size: 1.5rem;
	font-weight: 500;
	line-height: 120%;
}

.markdown:deep() h3 {
	font-size: 1.25rem;
	font-weight: 500;
	line-height: 120%;
}

.markdown:deep() h4 {
	font-weight: 700;
	font-size: 1rem;
	line-height: 247.5%;
}

.markdown:deep() ul,
.markdown:deep() ol {
	padding: 0;
	padding-inline-start: 0;
	margin-block-start: 0;
}

.markdown:deep() li {
	margin: 0 0 0 32px;
}

.markdown:deep() hr {
	border: none;
	border-top: 1px solid var(--separatorColor);
}

.markdown:deep() pre {
	background-color: var(--separatorColor);
	font-family: monospace;
	padding: 8px;
}

.markdown:deep() code {
	background-color: var(--separatorColor);
	font-family: monospace;
	padding: 2px;
}

.markdown:deep() pre > code {
	background-color: unset;
}

.markdown:deep() table {
	border-collapse: collapse;
}

.markdown:deep() th {
	padding: 8px;
	background: var(--separatorColor);
	border: 1px solid var(--separatorColor);
}

.markdown:deep() td {
	padding: 8px;
	border: 1px solid var(--separatorColor);
}

.markdown:deep() blockquote {
	padding: 8px;
	border-left: 5px solid var(--separatorColor);
}
</style>
