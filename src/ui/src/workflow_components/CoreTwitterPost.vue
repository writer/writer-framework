<template>
	<WorkflowsNodeBox :component="component" class="CoreTwitterPost">
		<div class="content"></div>
	</WorkflowsNodeBox>
</template>

<script lang="ts">
import { FieldControl, FieldType } from "../writerTypes";
import { computed, inject } from "vue";

export default {
	writer: {
		name: "Post to Twitter (X)",
		description: "Enables you to post to Twitter.",
		category: "Content",
		allowedParentTypes: ["workflow"],
		fields: {
			text: {
				name: "Text",
				type: FieldType.Text,
				control: FieldControl.Textarea,
			},
			accessToken: {
				name: "Access Token",
				type: FieldType.Text,
			},
			accessTokenSecret: {
				name: "Access Token Secret",
				type: FieldType.Text,
			},
			apiKey: {
				name: "API key",
				type: FieldType.Text,
			},
			apiKeySecret: {
				name: "API key secret",
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
				description: "If the operation fails.",
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

.CoreTwitterPost {
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
