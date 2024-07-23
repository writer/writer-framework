<template>
	<WorkflowsNodeBox :component="component" class="CoreSetState">
		I'm used to set state
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "Set state",
		description: "Set the value for a state element",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			element: {
				name: "State element",
				type: FieldType.Text,
			},
			value: {
				name: "Value",
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

.CoreSetState {
}
</style>
