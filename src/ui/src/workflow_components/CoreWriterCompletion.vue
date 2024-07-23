<template>
	<WorkflowsNodeBox :component="component" class="CoreWriterCompletion">
		I'm a Writer completion
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldControl, FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "Writer Completion",
		description: "Execute Writer completions",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			text: {
				name: "Text",
				type: FieldType.Text,
				control: FieldControl.Textarea,
				desc: "The text to complete.",
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

.CoreWriterCompletion {
}
</style>
