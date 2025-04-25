<template>
	<div
		class="BlueprintsNode"
		:class="{
			'BlueprintsNode--trigger': isTrigger,
			'BlueprintsNode--intelligent': isIntelligent,
			'BlueprintsNode--deprecated': isDeprecated,
			'BlueprintsNode--running': completionStyle == 'running',
			'BlueprintsNode--success': completionStyle == 'success',
			'BlueprintsNode--error': completionStyle == 'error',
		}"
	>
		<div
			v-if="isIntelligent && completionStyle === null"
			class="side"
		></div>
		<div class="extraBorder">
			<div v-if="completionStyle == 'running'" class="runner"></div>
		</div>
		<div class="main">
			<div class="title">
				<SharedImgWithFallback :urls="possibleImageUrls" />
				<BlueprintsNodeNamer
					:component-id="componentId"
					class="nodeNamer"
					:block-name="def.name"
				></BlueprintsNodeNamer>
				<div v-if="isDeprecated" class="deprecationNotice">
					Deprecated
				</div>
			</div>
			<div
				v-for="(outs, fieldKey) in dynamicOuts"
				:key="fieldKey"
				class="outputs"
			>
				<h4 v-if="def.fields?.[fieldKey]">
					{{ def.fields[fieldKey].name }}
				</h4>
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
					v-for="(out, outId) in { ...staticOuts, ...unknownOuts }"
					:key="outId"
					class="output"
				>
					<template v-if="outId !== 'trigger'">
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
		description: "A Blueprints node.",
		toolkit: "blueprints",
		category: "Other",
		fields: {
			alias: {
				name: "Alias",
				type: FieldType.Text,
			},
		},
		allowedParentTypes: ["blueprints_blueprint"],
		previewField: "alias",
	},
};
</script>
<script setup lang="ts">
import { computed, inject, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import { FieldType, WriterComponentDefinition } from "@/writerTypes";
import BlueprintsNodeNamer from "../base/BlueprintsNodeNamer.vue";
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

const isDeprecated = computed(() => {
	return def?.value?.deprecated;
});

const completionStyle = computed(() => {
	if (latestKnownOutcome.value == null) return null;
	if (latestKnownOutcome.value == "in_progress") return "running";

	// Any dynamic out is considered success

	return (
		{ ...staticOuts.value }?.[latestKnownOutcome.value]?.style ?? "success"
	);
});

const latestKnownOutcome = computed(() => {
	const logEntries = wfbm.getLogEntries();

	for (let i = 0; i < logEntries.length; i++) {
		const logEntry = logEntries[i];
		const we = logEntry.blueprintExecution;
		if (!we) continue;
		for (let j = 0; j < we.summary.length; j++) {
			const item = we.summary[j];
			if (item.componentId !== component.value.id) continue;
			return item.outcome;
		}
	}

	return null;
});

const isEngaged = computed(() => {
	const isSelected = wfbm.isComponentIdSelected(componentId);
	return isSelected;
});

const staticOuts = computed<WriterComponentDefinition["outs"]>(() => {
	const processedOuts = {};
	Object.entries(def.value.outs ?? {}).forEach(([outId, out]) => {
		if (out.style == "dynamic") return;
		processedOuts[outId] = out;
	});
	return processedOuts;
});

const unknownOuts = computed<WriterComponentDefinition["outs"]>(() => {
	const knownsOutIds = new Set([
		...Object.keys(staticOuts.value),
		...Object.values(dynamicOuts.value).flatMap(Object.keys),
	]);

	return (component.value?.outs ?? []).reduce<
		WriterComponentDefinition["outs"]
	>((acc, { outId }) => {
		if (knownsOutIds.has(outId)) return;
		acc[outId] = { name: outId, style: "dynamic", description: "" };
		return acc;
	}, {});
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
	Object.entries(def.value.outs ?? {}).forEach(([outId, out]) => {
		if (out.style !== "dynamic") {
			return;
		}
		if (!out.field) {
			processedOuts["default"] ??= {};
			processedOuts["default"][outId] = { ...out };
			return;
		}

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

function handleOutMousedown(ev: DragEvent, outId: string | number) {
	ev.stopPropagation();
	emit("outMousedown", outId);
}

const possibleImageUrls = computed(() => {
	if (["success", "error"].includes(completionStyle.value)) {
		const path = `/status/${completionStyle.value}.svg`;
		return [convertAbsolutePathtoFullURL(path)];
	}

	const paths = [
		`/components/${component.value.type}.svg`,
		`/components/blueprints_category_${def.value.category}.svg`,
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
.BlueprintsNode {
	background: var(--builderBackgroundColor);
	border-radius: 8px;
	width: 240px;
	position: absolute;
	box-shadow: var(--wdsShadowBox);
	user-select: none;
}

.BlueprintsNode--success {
	background: var(--wdsColorGreen3) !important;
}

.BlueprintsNode--error {
	background: var(--wdsColorOrange2) !important;
}

.BlueprintsNode--running {
	box-shadow: 0px 2px 24px -16px #6985ff;
	animation: shadowPulse 1s infinite alternate ease-in-out;
}

.BlueprintsNode--deprecated {
	filter: grayscale(1);
}

@keyframes shadowPulse {
	0% {
		box-shadow: 0px 2px 24px -16px #6985ff;
	}
	100% {
		box-shadow: 0px 2px 24px -4px #bfcbff;
	}
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

.BlueprintsNode:hover .extraBorder {
	background-color: var(--wdsColorBlue2);
}

.BlueprintsNode--intelligent:hover .extraBorder {
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%)
	);
}

.BlueprintsNode.selected.component .extraBorder {
	background: var(--wdsColorBlue4);
}

.extraBorder .runner {
	height: 200%;
	width: 200%;
	position: absolute;
	top: -50%;
	left: -50%;
	background: conic-gradient(#6985ff, #f5f5f9);
	filter: blur(24px);
	animation: spin 1.5s linear infinite;
}

.BlueprintsNode--intelligent .extraBorder .runner {
	background: conic-gradient(#6985ff, #ffd5f8, #bfcbff);
}

.main {
	position: relative;
	margin: 2px;
	background: var(--builderBackgroundColor);
	border-radius: 6px;
}

.BlueprintsNode--intelligent .main {
	margin-left: 8px;
	border-radius: 0 6px 6px 0;
}

.BlueprintsNode--trigger,
.BlueprintsNode--trigger .main,
.BlueprintsNode--trigger .extraBorder {
	border-radius: 36px;
}

.title {
	display: grid;
	gap: 10px;
	padding: 12px;
	border-radius: 12px 12px 0 0;
	align-items: center;
	grid-template-columns: 24px 1fr;
}

.BlueprintsNode--intelligent .title {
	padding-left: 6px;
}

.title img {
	width: 24px;
	height: 24px;
}

.title .deprecationNotice {
	font-size: 12px;
	text-transform: uppercase;
	font-size: 12px;
	font-weight: 500;
	line-height: 12px; /* 100% */
	letter-spacing: 1.3px;
	text-transform: uppercase;
	color: var(--builderSecondaryTextColor);
}

.BlueprintsNode--trigger .title img {
	border-radius: 50%;
}

.BlueprintsNode:hover .nodeNamer :deep(.blockName) {
	background: var(--builderSubtleSeparatorColor);
}

.BlueprintsNode:hover .nodeNamer :deep(.aliasEditor) {
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

.BlueprintsNode--trigger .outputs {
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

.output .ball.branching {
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
