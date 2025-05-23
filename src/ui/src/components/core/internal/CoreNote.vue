<script lang="ts">
import {
	FieldControl,
	FieldType,
	WriterComponentDefinition,
} from "@/writerTypes";

const definition: WriterComponentDefinition = {
	name: "Note",
	description: "Internal note displayed only in edit mode",
	category: "Internal",
	fields: {
		parentInstancePath: {
			name: "Parent's instance path",
			type: FieldType.Text,
		},
		content: {
			name: "Content",
			type: FieldType.Text,
			control: FieldControl.Textarea,
		},
		createdAt: {
			name: "Created At",
			type: FieldType.Text,
		},
		createdBy: {
			name: "Created By",
			type: FieldType.Number,
		},
	},
};

export default {
	writer: definition,
};
</script>

<template>
	<span v-if="false"
		><!-- we need that the component contains a template --></span
	>
</template>
