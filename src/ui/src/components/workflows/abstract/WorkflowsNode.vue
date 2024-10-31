<template>
	<div class="WorkflowsNode">
		<div class="title">
			<img
				src="data:image/png;base64,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"
			/>
			{{ def.name }}
		</div>
		<div v-if="false" class="main">
			<div></div>
		</div>
		<div class="outputs">
			<div
				v-for="(out, outId) in { ...dynamicOuts, ...staticOuts }"
				:key="outId"
				class="output"
			>
				{{ out.name }}
				<div
					class="ball"
					:class="out.style"
					:data-writer-socket-id="outId"
					:data-writer-unselectable="true"
					@click.capture.stop
					@mousedown.capture="
						(ev: DragEvent) => handleOutMousedown(ev, outId)
					"
				></div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
export default {
	writer: {
		name: "Node",
		description: "A Workflows node.",
		toolkit: "workflows",
		category: "Other",
		fields: {},
		allowedParentTypes: ["workflows_workflow"],
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { computed, inject, watch } from "vue";
import injectionKeys from "@/injectionKeys";

const emit = defineEmits(["outMousedown", "engaged"]);
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const fields = inject(injectionKeys.evaluatedFields);

const def = computed(() => {
	const component = wf.getComponentById(componentId);
	return wf?.getComponentDefinition(component.type);
});

const isEngaged = computed(() => {
	const isSelected = wfbm.getSelectedId() == componentId;
	return isSelected;
});

const staticOuts = computed(() => {
	const processedOuts = {};
	Object.entries(def.value.outs).forEach(([outId, out]) => {
		if (outId === "$dynamic") return;
		processedOuts[outId] = out;
	});
	return processedOuts;
});

const dynamicOuts = computed(() => {
	const processedOuts = {};
	Object.entries(def.value.outs).forEach(([outId, out]) => {
		if (outId !== "$dynamic") return;
		const dynamicField = out.field;
		const dynamicKeys = Object.keys(fields[dynamicField].value ?? {});
		dynamicKeys.forEach((key) => {
			processedOuts[`${outId}_${key}`] = {
				name: key,
				description: "Dynamically created",
				style: "dynamic",
			};
		});
	});
	return processedOuts;
});

function handleOutMousedown(ev: DragEvent, outId: string) {
	ev.stopPropagation();
	emit("outMousedown", outId);
}

watch(isEngaged, () => {
	emit("engaged");
});
</script>

<style scoped>
.WorkflowsNode {
	background: var(--builderBackgroundColor);
	border: 2px solid transparent;
	border-radius: 8px;
	width: 240px;
	position: absolute;
	box-shadow: 0px 2px 0px 0px #f3f3f3;
	user-select: none;
}

.WorkflowsNode:not(.selected) {
	transition: border-color 0.2s ease-in-out;
}

.WorkflowsNode:hover {
	border: 2px solid #e4e9ff;
}

.title {
	display: flex;
	gap: 12px;
	padding: 12px;
	border-radius: 12px 12px 0 0;
	align-items: center;
	font-size: 14px;
	font-style: normal;
	font-weight: 500;
	line-height: 140%;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.title img {
	width: 30px;
}

.main {
	font-size: 14px;
	padding: 16px 12px 16px 12px;
}

.outputs {
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
	font-size: 12px;
	font-style: normal;
	font-weight: 400;
	/* letter-spacing: 1.3px; */
	/* text-transform: uppercase; */
	color: #4f4f4f;
	font-feature-settings:
		"liga" off,
		"clig" off;
}

.output .ball {
	margin-right: -9px;
	height: 16px;
	width: 16px;
	border-radius: 50%;
	border: 1px solid var(--builderBackgroundColor);
	cursor: pointer;
}

.output .ball.success {
	background: #3bdcab;
}

.output .ball.error {
	background: #ff643c;
}

.output .ball.dynamic {
	background: #a95ef8;
}

.WorkflowsNode.selected.component {
	border: 2px solid #6985ff;
	background: var(--builderBackgroundColor);
}
</style>
