<template>
	<WorkflowsNode v-if="isWorkflowNode" :draggable="false" />
	<div v-else class="RenderError" :draggable="draggable">
		<div class="title">
			<h2>Error rendering {{ componentType }}</h2>
		</div>
		<div class="message">
			{{ message }}
		</div>
	</div>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import { computed, inject, PropType } from "vue";

import WorkflowsNode from "@/components/workflows/abstract/WorkflowsNode.vue";

defineProps({
	componentType: {
		type: String as PropType<Component["type"]>,
		required: true,
	},
	message: { type: String, required: true },
	draggable: { type: Boolean, required: false },
});

const wf = inject(injectionKeys.core);
const componentId = inject(injectionKeys.componentId);

const component = computed(() => wf.getComponentById(componentId));
const parent = computed(() => wf.getComponentById(component.value?.parentId));

const isWorkflowNode = computed(
	() => parent.value?.type === "workflows_workflow",
);
</script>

<style scoped></style>
