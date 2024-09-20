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
			<div v-for="(out, outId) in outs" :key="outId" class="output">
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
const componentId = inject(injectionKeys.componentId);
const fields = inject(injectionKeys.evaluatedFields);

const def = computed(() => {
	const component = wf.getComponentById(componentId);
	return wf?.getComponentDefinition(component.type);
});

const outs = computed(() => {
	const processedOuts = {};
	Object.entries(def.value.outs).forEach(([outId, out]) => {
		if (outId !== "$") {
			processedOuts[outId] = out;
			return;
		}
		const dynamicField = out.field;
		const dynamicKeys = Object.keys(fields[dynamicField].value ?? {});
		dynamicKeys.forEach((key) => {
			processedOuts[key] = {
				name: key,
				description: "Dynamically created",
				style: "success",
			};
		});
	});
	return processedOuts;
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

.title {
	display: flex;
	gap: 12px;
	padding: 14px 16px 14px 16px;
	border-radius: 12px 12px 0 0;
	border-top: 1px solid var(--builderSeparatorColor);
	border-left: 1px solid var(--builderSeparatorColor);
	border-right: 1px solid var(--builderSeparatorColor);
	align-items: center;
	font-size: 12px;
	font-style: normal;
	font-weight: 500;
	line-height: 12px;
	letter-spacing: 1.3px;
	text-transform: uppercase;
}

.title img {
	width: 18px;
}

.title i {
	font-size: 16px;
}

.main {
	font-size: 14px;
	padding: 12px 16px 12px 16px;
	border-left: 1px solid var(--builderSeparatorColor);
	border-right: 1px solid var(--builderSeparatorColor);
}

.outputs {
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 0 0 12px 12px;
	display: flex;
	flex-direction: column;
	gap: 8px;
	padding: 12px 0 12px 16px;
}

.output {
	display: flex;
	gap: 8px;
	align-items: center;
	justify-content: right;
	font-size: 10px;
	font-style: normal;
	font-weight: 500;
	letter-spacing: 1.3px;
	text-transform: uppercase;
}

.output .ball {
	margin-right: -8px;
	height: 16px;
	width: 16px;
	border-radius: 50%;
	border: 1px solid var(--builderBackgroundColor);
	cursor: pointer;
}

.output .ball.success {
	background: var(--builderSuccessColor);
}

.output .ball.error {
	background: var(--builderErrorColor);
}
</style>
