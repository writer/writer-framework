<template>
	<WorkflowsNodeBox :component="component" class="CoreHTTPCall">
		<div class="content">
			<div class="method">
				{{ fields.method.value?.toUpperCase() }}
			</div>
			<div class="url">
				{{ fields.url.value }}
			</div>
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
	gap: 4px;
}

.method {
	background-color: #b5eeee;
	padding: 2px 4px 2px 4px;
	border-radius: 4px;
	display: inline;
}

.url {
}
</style>
