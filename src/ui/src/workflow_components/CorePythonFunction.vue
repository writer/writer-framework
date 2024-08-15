<template>
	<WorkflowsNodeBox
		:component="component"
		variant="tool"
		class="CorePythonFunction"
	>
		I'm a Python function
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "Python function",
		description: "Run Python functions",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			functionName: {
				name: "Function name",
				type: FieldType.Object,
			},
		},
		outs: {
			success: {
				name: "Success",
				description: "If the function doesn't raise an Exception.",
				style: "success",
			},
			exception: {
				name: "Exception",
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

.CorePythonFunction {
}
</style>
