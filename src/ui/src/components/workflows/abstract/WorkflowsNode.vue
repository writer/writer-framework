<template>
	<div
		class="WorkflowsNode"
		:class="{
			'WorkflowsNode--trigger': isTrigger,
			'WorkflowsNode--intelligent': isIntelligent,
			'WorkflowsNode--running': isRunning,
		}"
	>
		<div v-if="isIntelligent" class="side"></div>
		<div class="extraBorder">
			<div v-if="isRunning" class="runner"></div>
		</div>
		<div class="main">
			<div class="title">
				<SharedImgWithFallback :urls="possibleImageUrls" />
				<WorkflowsNodeNamer
					:component-id="componentId"
					class="nodeNamer"
					:block-name="def.name"
				></WorkflowsNodeNamer>
			</div>
			<div
				v-for="(outs, fieldKey) in dynamicOuts"
				:key="fieldKey"
				class="outputs"
			>
				<h4>{{ def.fields[fieldKey].name }}</h4>
				<div v-for="(out, outId) in outs" :key="outId" class="output">
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
				<div v-if="Object.keys(outs).length == 0">None configured.</div>
			</div>
			<div class="outputs">
				<div
					v-for="(out, outId) in staticOuts"
					:key="outId"
					class="output"
				>
					<template v-if="Object.keys(staticOuts).length > 1">
						{{ out.name }}
					</template>
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
	</div>
</template>

<script lang="ts">
export default {
	writer: {
		name: "Node",
		description: "A Workflows node.",
		toolkit: "workflows",
		category: "Other",
		fields: {
			alias: {
				name: "Alias",
				type: FieldType.Text,
			},
		},
		allowedParentTypes: ["workflows_workflow"],
		previewField: "alias",
	},
};
</script>
<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import { Component, FieldType, WriterComponentDefinition } from "@/writerTypes";
import WorkflowsNodeNamer from "../base/WorkflowsNodeNamer.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

const emit = defineEmits(["outMousedown", "engaged"]);
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const fields = inject(injectionKeys.evaluatedFields);
const isRunning = ref(false);

const component = computed(() => {
	const component = wf.getComponentById(componentId);
	return component;
});

const def = computed(() => {
	return wf?.getComponentDefinition(component.value?.type);
});

const isTrigger = computed(() => {
	return def?.value?.category == "Triggers";
});

const isIntelligent = computed(() => {
	return def?.value?.category == "Writer";
});

const isEngaged = computed(() => {
	const isSelected = wfbm.isComponentIdSelected(componentId);
	return isSelected;
});

const staticOuts = computed<WriterComponentDefinition["outs"]>(() => {
	const processedOuts = {};
	Object.entries(def.value.outs).forEach(([outId, out]) => {
		if (out.field) return;
		processedOuts[outId] = out;
	});
	return processedOuts;
});

function getDynamicKeysFromField(fieldKey: string) {
	const fieldType = def.value.fields[fieldKey].type;
	const isToolsField = fieldType == FieldType.Tools;
	const keys = Object.keys(fields[fieldKey].value ?? {});
	if (!isToolsField) return keys;
	const functionCallKeys = keys.filter(
		(k) => fields[fieldKey].value[k]?.type == "function",
	);
	return functionCallKeys;
}

const dynamicOuts = computed<
	Record<
		keyof WriterComponentDefinition["fields"],
		WriterComponentDefinition["outs"]
	>
>(() => {
	const processedOuts = {};
	Object.entries(def.value.outs).forEach(([outId, out]) => {
		if (!out.field) return;
		processedOuts[out.field] = {};
		const dynamicKeys = getDynamicKeysFromField(out.field);
		dynamicKeys.forEach((key) => {
			processedOuts[out.field][`${outId}_${key}`] = {
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

const possibleImageUrls = computed(() => {
	const paths = [
		`/components/${component.value.type}.svg`,
		`/components/workflows_category_${def.value.category}.svg`,
	];

	if (wf.featureFlags.value.includes("custom_block_icons")) {
		paths.unshift(`/static/components/${component.value.id}.svg`);
	}

	return paths.map((p) => convertAbsolutePathtoFullURL(p));
});

type WorkflowActivity = {
	componentId: Component["id"];
	type: "start" | "finish";
};

function handleWorkflowActivityMail(payload: WorkflowActivity) {
	if (payload.componentId !== component.value.id) return;
	if (payload.type == "start") {
		console.log("up", payload.componentId);
		isRunning.value = true;
		return;
	}
	if (payload.type == "finish") {
		console.log("taking down", payload.componentId);
		setTimeout(() => {
			isRunning.value = false;
		}, 200);

		return;
	}
}

onMounted(() => {
	wf.addMailSubscription("workflowActivity", handleWorkflowActivityMail);
});

onUnmounted(() => {
	wf.removeMailSubscription("workflowActivity", handleWorkflowActivityMail);
});

watch(isEngaged, () => {
	emit("engaged");
});
</script>

<style scoped>
.WorkflowsNode {
	background: var(--builderBackgroundColor);
	border-radius: 8px;
	width: 240px;
	position: absolute;
	box-shadow: var(--wdsShadowBox);
	user-select: none;
}

.side {
	position: absolute;
	border-radius: 8px 0 0 8px;
	left: 0;
	top: 0;
	bottom: 0;
	width: 8px;
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(180deg, #ffd5f8 0%, #bfcbff 95.5%)
	);
}

.extraBorder {
	height: 100%;
	width: 100%;
	border-radius: 8px;
	overflow: hidden;
	position: absolute;
	top: 0;
	left: 0;
}

.WorkflowsNode:hover .extraBorder {
	background-color: var(--wdsColorBlue2);
}

.WorkflowsNode--intelligent:hover .extraBorder {
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%)
	);
}

.WorkflowsNode.selected.component .extraBorder {
	background: var(--wdsColorBlue4);
}

.extraBorder .runner {
	height: 200%;
	width: 200%;
	position: absolute;
	top: -50%;
	left: -50%;
	background: conic-gradient(#a95ef8, #f5f5f9);
	filter: blur(24px);
	animation: spin 0.8s linear infinite;
}

.main {
	position: relative;
	margin: 2px;
	background: var(--builderBackgroundColor);
	border-radius: 6px;
}

.WorkflowsNode--intelligent .main {
	margin-left: 6px;
	border-radius: 0 6px 6px 0;
}

.WorkflowsNode--trigger,
.WorkflowsNode--trigger .main,
.WorkflowsNode--trigger .extraBorder {
	border-radius: 36px;
}

.title {
	display: flex;
	gap: 10px;
	padding: 12px;
	border-radius: 12px 12px 0 0;
	align-items: center;
}

.title img {
	width: 24px;
	height: 24px;
}

.WorkflowsNode--trigger .title img {
	border-radius: 50%;
}

.WorkflowsNode:hover .nodeNamer :deep(.blockName) {
	background: var(--builderSubtleSeparatorColor);
}

.WorkflowsNode:hover .nodeNamer :deep(.aliasEditor) {
	background: var(--builderSubtleSeparatorColor);
}

.outputs {
	border-radius: 0 0 12px 12px;
	display: flex;
	flex-direction: column;
	gap: 8px;
	padding: 12px 0 12px 16px;
	border-top: 1px solid var(--builderSeparatorColor);
	font-size: 12px;
}

.WorkflowsNode--trigger .outputs {
	border: none;
	position: absolute;
	right: 0;
	top: 0;
	bottom: 0;
	padding: 0;
	height: 100%;
	justify-content: center;
}

.output {
	display: flex;
	gap: 8px;
	align-items: center;
	justify-content: right;
	font-size: 12px;
	font-style: normal;
	font-weight: 400;
	color: var(--wdsColorGray5);
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
	background: var(--wdsColorGreen5);
}

.output .ball.error {
	background: var(--wdsColorOrange5);
}

.output .ball.dynamic {
	background: var(--wdsColorPurple4);
}

@keyframes spin {
	0% {
		transform: rotate(0deg);
		transform-origin: center;
	}
	100% {
		transform: rotate(360deg);
		transform-origin: center;
	}
}
</style>
