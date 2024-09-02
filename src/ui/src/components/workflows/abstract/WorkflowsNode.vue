<docs lang="md">
    Represents a node in Writer Framework Workflows.
</docs>

<template>
	<div class="WorkflowsNode">
		<div class="title">
			<i class="material-symbols-outlined">settings</i>
			{{ def.name }}
		</div>
		<div class="main">
			<div></div>
		</div>
		<div class="outputs">
			<div v-for="(out, outId) in def.outs" :key="outId" class="output">
				{{ out.name }}
				<div
					class="ball"
					:class="out.style"
					:data-writer-socket-id="outId"
					:data-writer-unselectable="true"
					@click.capture="
						(ev: DragEvent) => handleOutClick(ev, outId)
					"
				></div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "@/writerTypes";

export default {
	writer: {
		name: "Node",
		description: "A Workflows node.",
		toolkit: "workflows",
		category: "Other",
		fields: {
			text: {
				name: "Text",
				init: "Button Text",
				type: FieldType.Text,
			},
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { computed, inject } from "vue";
import { Component } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);

const def = computed(() => {
	return wf?.getComponentDefinition("workflowsnode");
});

const emit = defineEmits(["outSelect"]);

function handleOutClick(ev: DragEvent, outId: string) {
	ev.stopPropagation();
	emit("outSelect", outId);
}
</script>

<style scoped>
.WorkflowsNode {
	background: var(--builderBackgroundColor);
	border-radius: 12px;
	width: 240px;
	position: absolute;
	box-shadow: 0px 2px 0px 0px rgba(0, 0, 0, 0.03);
}
</style>
