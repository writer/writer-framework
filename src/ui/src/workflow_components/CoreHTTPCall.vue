<template>
	<WorkflowsNodeBox
		:component="component"
		variant="tool"
		class="CoreHTTPCall"
	>
		<div class="content">
			<span class="method">
				{{ fields.method.value?.toUpperCase() }}
			</span>
			<span class="url">
				{{ fields.url.value }}
			</span>
		</div>
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "HTTP call",
		description: "Execute HTTP calls",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			url: {
				name: "URL",
				type: FieldType.Text,
			},
			method: {
				name: "Method",
				type: FieldType.Text,
				options: {
					get: "GET",
					put: "PUT",
					post: "POST",
					delete: "DELETE",
				},
				default: "get",
			},
		},
		outs: {
			success: {
				name: "Success",
				description: "If the function doesn't raise an Exception.",
				style: "success",
			},
			responseError: {
				name: "Response Error",
				description: "If the function raises an Exception.",
				style: "error",
			},
			connectionError: {
				name: "Connection Error",
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
const fields = inject(injectionKeys.evaluatedFields);

const component = computed(() => wf.getComponentById(componentId));
</script>

<style scoped>
@import "../renderer/sharedStyles.css";

.CoreHTTPCall {
}

.content {
	display: block;
}

.method {
	background-color: #f0f0f0;
	padding: 2px 4px 2px 4px;
	margin: 2px 0 2px 0;
	border-radius: 4px;
	display: inline-block;
}

.url {
}
</style>
