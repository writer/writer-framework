<template>
	<WorkflowsNodeBox :component="component" class="CoreWriterKGAdd">
		I'm a Writer KG node
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldControl, FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "Add File to Writer KG",
		description: "Add file to an existing Writer Knowledge Graph",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			text: {
				name: "Text",
				type: FieldType.Text,
				control: FieldControl.Textarea,
				desc: "The text to complete.",
			},
			modelId: {
				name: "Model",
				type: FieldType.Text,
				options: {
					"palmyra-x-003-instruct": "palmyra-x-003-instruct",
					"palmyra-x-002-instruct": "palmyra-x-002-instruct",
					"palmyra-x-32k-instruct": "palmyra-x-32k-instruct",
					"palmyra-x-002-32k": "palmyra-x-002-32k",
					"palmyra-med-32k": "palmyra-med-32k",
					"palmyra-med": "palmyra-med",
					"palmyra-fin-32k": "palmyra-fin-32k",
				},
				init: "palmyra-x-002-instruct",
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

.CoreWriterKGAdd
</style>
