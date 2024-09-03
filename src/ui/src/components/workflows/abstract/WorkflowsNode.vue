<docs lang="md">
    Represents a node in Writer Framework Workflows.
</docs>

<template>
	<div></div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";

export default {
	writer: {
		name: "Node",
		toolkit: "workflows",
		category: "Other",
		fields: {
			text: {
				name: "Text",
				init: "Button Text",
				type: FieldType.Text,
			},
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { ComponentPublicInstance, inject, ref } from "vue";
</script>

<style scoped></style>
