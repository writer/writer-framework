<template>
	<div class="CoreHeader">
		<h1>{{ fields.text.value }}</h1>
		<div class="container horizontal" data-writer-container>
			<slot></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "@/writerTypes";
import { cssClasses, primaryTextColor } from "@/renderer/sharedStyleFields";

const description =
	"A container component that typically contains the main navigation elements.";

export default {
	writer: {
		name: "Header",
		description,
		category: "Layout",
		allowedChildrenTypes: ["*"],
		fields: {
			text: {
				name: "Text",
				init: "Header Text",
				default: "(No text)",
				type: FieldType.Text,
			},
			primaryTextColor,
			cssClasses,
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "@/injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "@/renderer/sharedStyles.css";

.CoreHeader {
	display: flex;
	flex-wrap: wrap;
	gap: 16px;
	max-width: 100%;
	color: var(--primaryTextColor);
}

h1 {
	line-height: 4rem;
}

.container {
	max-width: 100%;
	flex: 2 0 auto;
	align-items: center;
	justify-content: right;
	flex-wrap: wrap;
}
</style>
