<template>
	<div
		class="WorkflowsNode"
		:class="{
			'WorkflowsNode--trigger': isTrigger,
			'WorkflowsNode--intelligent': isIntelligent,
		}"
	>
		<div class="main">
			<div v-if="isIntelligent" class="side"></div>
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
import { computed, inject, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import { FieldType, WriterComponentDefinition } from "@/writerTypes";
import WorkflowsNodeNamer from "../base/WorkflowsNodeNamer.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

const emit = defineEmits(["outMousedown", "engaged"]);
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const fields = inject(injectionKeys.evaluatedFields);

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

.WorkflowsNode--intelligent {
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%)
	);
}

.side {
	position: absolute;
	border-radius: 8px 0 0 8px;
	left: 0px;
	top: 0px;
	bottom: 0px;
	width: 8px;
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(180deg, #ffd5f8 0%, #bfcbff 95.5%)
	);
}

.WorkflowsNode:hover .side,
.WorkflowsNode.selected.component .side {
	border-radius: 6px 0 0 6px;
	width: 6px;
	left: 2px;
	top: 2px;
	bottom: 2px;
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(180deg, #ffd5f8 0.01%, #bfcbff 99.42%)
	);
}

.main {
	padding: 2px;
	background: var(--builderBackgroundColor);
	border-radius: 6px;
}

.WorkflowsNode:hover {
	padding: 2px;
	background-color: var(--wdsColorBlue2);
}

.WorkflowsNode:hover .main {
	padding: 0px;
}

.WorkflowsNode--trigger {
	border-radius: 36px;
}

.WorkflowsNode--trigger .main {
	border-radius: 36px;
}

.WorkflowsNode.selected.component {
	padding: 2px;
	background: var(--wdsColorBlue4);
}

.WorkflowsNode.selected.component .main {
	padding: 0;
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
</style>
