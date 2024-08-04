<template>
	<WorkflowsNodeBox :component="component" class="CoreCreateFile">
		I'm used to create files from content
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "Create file",
		description: "Create a file from content",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			fileName: {
				name: "File name",
				type: FieldType.Text,
			},
			content: {
				name: "Content",
				type: FieldType.Text,
			},
			fileType: {
				name: "File type",
				type: FieldType.Text,
			},
		},
		outs: {
			success: {
				name: "Success",
				description: "If the function doesn't raise an Exception.",
				style: "success",
			},
			error: {
				name: "Error",
				description: "If the function raises an Exception.",
				style: "error",
			},
		},
	},
};
</script>
<script setup lang="ts">
import WorkflowsNodeBox from "./WorkflowsNodeBox.vue";
import injectionKeys from "../injectionKeys";

const wf = inject(injectionKeys.core);
const componentId = inject(injectionKeys.componentId);

const component = computed(() => wf.getComponentById(componentId));
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreCreateFile {
}
</style>
