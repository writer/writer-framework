<template>
	<div
		class="BlueprintsNode"
		:class="{
			'BlueprintsNode--trigger': isTrigger,
			'BlueprintsNode--intelligent': isIntelligent,
			'BlueprintsNode--deprecated': isDeprecated,
			'BlueprintsNode--running': completionStyle == 'running',
			'BlueprintsNode--success': completionStyle == 'success',
			'BlueprintsNode--skipped': completionStyle == 'skipped',
			'BlueprintsNode--stopped': completionStyle == 'stopped',
			'BlueprintsNode--error': completionStyle == 'error',
		}"
		@dblclick="handleDoubleClick"
	>
		<div
			v-if="isIntelligent && completionStyle === null"
			class="BlueprintsNode__side"
		></div>
		<div class="BlueprintsNode__extraBorder">
			<div v-if="completionStyle == 'running'" class="runner"></div>
		</div>
		<div class="BlueprintsNode__main">
			<div class="BlueprintsNode__main__title">
				<SharedImgWithFallback
					:urls="possibleImageUrls"
					class="icon"
					:loader-max-width-px="24"
					:loader-max-height-px="24"
				/>
				<BlueprintsNodeNamer
					:component-id="componentId"
					class="nodeNamer"
					:block-name="displayName"
				></BlueprintsNodeNamer>
				<div v-if="isDeprecated" class="deprecationNotice">
					Deprecated
				</div>
				<BlueprintsNodeActions
					v-if="isTrigger"
					:show-display-error-option="canDisplayErrorOut"
					@show-error="forceDisplayErrorOut = true"
				/>
			</div>
			<div
				v-for="(outs, fieldKey) in dynamicOuts"
				:key="fieldKey"
				class="BlueprintsNode__main__outputs"
			>
				<h4
					v-if="def.fields?.[fieldKey]"
					class="BlueprintsNode__main__outputs__title"
				>
					{{ def.fields[fieldKey].name }}
				</h4>
				<BlueprintsNodeOutput
					v-for="(out, outId) in outs"
					:key="outId"
					class="BlueprintsNode__main__outputs__output"
					:out-id="outId"
					:out="out"
					display-label
					@click="$emit('outMousedown', outId)"
				/>
				<BlueprintsNodeTools
					:field-key="fieldKey"
					:field-type="def.fields?.[fieldKey]?.type ?? ''"
					:field-value="fields[fieldKey]?.value"
					:has-outputs="Object.keys(outs).length > 0"
				/>
			</div>
			<div
				v-if="Object.keys(staticOuts).length > 0"
				class="BlueprintsNode__main__outputs"
				:class="{
					'BlueprintsNode__main__outputs--float':
						hasOnlySuccessOut && !isTrigger,
				}"
			>
				<h4
					v-if="shouldShowStaticOutLabel"
					class="BlueprintsNode__main__outputs__title"
				>
					{{ staticOutLabel }}
				</h4>
				<BlueprintsNodeOutput
					v-for="(out, outId) in staticOuts"
					:key="outId"
					class="BlueprintsNode__main__outputs__output"
					:out-id="outId"
					:out="out"
					:display-label="!hasOnlySuccessOut"
					@click="$emit('outMousedown', outId)"
				/>
				<BlueprintsNodeOutput
					v-for="(out, outId) in unknownOuts"
					:key="outId"
					class="BlueprintsNode__main__outputs__output"
					:out-id="outId"
					:out="out"
					display-label
					@click="$emit('outMousedown', outId)"
				/>
			</div>
			<div v-if="!isTrigger" class="BlueprintsNode__main__footer">
				<BlueprintsNodeLogs
					v-if="latestKnownOutcomes.length > 0"
					:completion-style
					:count="latestKnownOutcomes.length"
					@click="openLogs"
				/>
				<BlueprintsNodeActions
					:show-display-error-option="canDisplayErrorOut"
					:show-open-editor-option="isCodeComponent"
					@show-error="forceDisplayErrorOut = true"
				/>
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
import { computed, inject, nextTick, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import { FieldType, WriterComponentDefinition } from "@/writerTypes";
import BlueprintsNodeNamer from "../base/BlueprintsNodeNamer.vue";
import { useComponentActions } from "@/builder/useComponentActions";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { useComponentInformation } from "@/composables/useComponentInformation";
import BlueprintsNodeActions from "./BlueprintsNodeActions.vue";
import BlueprintsNodeOutput from "./BlueprintsNodeOutput.vue";
import BlueprintsNodeLogs from "./BlueprintsNodeLogs.vue";
import BlueprintsNodeTools from "./BlueprintsNodeTools.vue";
import { useBlueprintNodeTools } from "@/composables/useBlueprintNodeTools";
import { getSourceBlueprintName } from "@/builder/useComponentDescription";
import { useToasts } from "@/builder/useToast";
import { useWriterTracking } from "@/composables/useWriterTracking";

const emit = defineEmits(["outMousedown", "engaged"]);
const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { removeOut, goToComponentParentPage } = useComponentActions(wf, wfbm);
const { pushToast } = useToasts();
const tracking = useWriterTracking(wf);
const componentId = inject(injectionKeys.componentId);
const fields = inject(injectionKeys.evaluatedFields);

const isTrigger = computed(() => {
	return def?.value?.category == "Triggers";
});

const isIntelligent = computed(() => {
	return def?.value?.category == "Writer";
});

const isDeprecated = computed(() => {
	return def?.value?.deprecated;
});

const { component, definition: def } = useComponentInformation(wf, componentId);

const isCodeComponent = computed(() => {
	return component.value?.type === "blueprints_code";
});

const displayName = computed(() => {
	if (!component.value) return "Unknown";
	return (
		getSourceBlueprintName(wf, component.value) ||
		def.value?.name ||
		"Unknown"
	);
});

const completionStyle = computed(() => {
	if (latestKnownOutcome.value == null) return null;
	if (latestKnownOutcome.value == "skipped") return "skipped";
	if (latestKnownOutcome.value == "stopped") return "stopped";
	if (latestKnownOutcome.value == "in_progress") return "running";

	// Any dynamic out is considered success
	return def.value?.outs?.[latestKnownOutcome.value]?.style ?? "success";
});

const { hasOnlyNonFunctionTools } = useBlueprintNodeTools(
	computed(() => def.value),
	fields,
);

const hasDynamicNonToolOutputs = computed(() => {
	const dynamicOutsEntries = Object.entries(def.value.outs ?? {});
	return dynamicOutsEntries.some(([_, out]) => {
		if (out.style !== "dynamic" || !out.field) return false;
		const fieldType = def.value.fields?.[out.field]?.type;
		return fieldType !== FieldType.Tools;
	});
});

const staticOutLabel = computed(() => {
	if (hasDynamicNonToolOutputs.value) return "OR";
	if (hasOnlyNonFunctionTools.value) return "No outputs";
	return "THEN";
});

const shouldShowStaticOutLabel = computed(() => {
	return (
		hasOnlyNonFunctionTools.value ||
		(!hasOnlySuccessOut.value && Object.keys(dynamicOuts.value).length > 0)
	);
});

const latestRun = computed(() => {
	const logEntries = wfbm.getLogEntries();
	const runId =
		logEntries.find((entry) => {
			return !!entry.blueprintExecution;
		})?.blueprintExecution?.runId ?? null;
	return logEntries.filter((entry) => {
		return entry?.blueprintExecution?.runId === runId;
	});
});

const outcomeSeverity = {
	in_progress: 5,
	error: 4,
	success: 3,
	stopped: 2,
	skipped: 1,
	none: 0,
};

const latestKnownOutcomes = computed(() => {
	const executionLogs = latestRun.value
		.map((entry) => {
			return entry.blueprintExecution;
		})
		.filter(Boolean);
	return executionLogs.flatMap((log) => {
		return log.summary
			.filter((item) => item.componentId === component.value.id)
			.filter((item) => Boolean(item.outcome));
	});
});

const latestKnownOutcome = computed(() => {
	let outcome = "none";

	for (const item of latestKnownOutcomes.value) {
		const severity =
			outcomeSeverity[item.outcome] ?? outcomeSeverity.success;
		if (severity > outcomeSeverity[outcome]) {
			outcome = item.outcome;
		}
	}

	return outcome === "none" ? null : outcome;
});

const isEngaged = computed(() => {
	const isSelected = wfbm.isComponentIdSelected(componentId);
	return isSelected;
});

const forceDisplayErrorOut = ref(false);

const canDisplayErrorOut = computed(() => {
	if (!hasErrorOut.value) return false;
	if (shouldDisplayError.value) return false;
	return !forceDisplayErrorOut.value;
});

const hasErrorOut = computed(() => def.value?.outs?.["error"] !== undefined);

const shouldDisplayError = computed(() => {
	if (!hasErrorOut.value) return false;

	const isConnected = component.value.outs?.some((o) => o.outId === "error");
	if (isConnected) return true;

	return forceDisplayErrorOut.value;
});

const hasOnlySuccessOut = computed(() => {
	if (Object.keys(dynamicOuts.value ?? {}).length > 0) return false;
	if (Object.keys(unknownOuts.value ?? {}).length > 0) return false;
	if (Object.keys(staticOuts.value ?? {}).length > 1) return false;
	return true;
});

const staticOuts = computed<WriterComponentDefinition["outs"]>(() => {
	return Object.entries(def.value.outs ?? {}).reduce<
		WriterComponentDefinition["outs"]
	>((acc, [outId, out]) => {
		if (out.style == "dynamic") return acc;

		if (outId === "error" && !shouldDisplayError.value) return acc;

		acc[outId] = out;
		return acc;
	}, {});
}, {});

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

watch(
	dynamicOuts,
	() => {
		const allDynamicOuts = Object.values(dynamicOuts.value).flatMap(
			Object.keys,
		);

		const outsToRemove =
			component.value?.outs?.filter(
				(out) =>
					!allDynamicOuts.includes(out.outId) &&
					!(out.outId in staticOuts.value),
			) ?? [];

		outsToRemove.forEach((out) => {
			if (component.value) {
				removeOut(component.value.id, out);
			}
		});
	},
	{ immediate: true },
);

const possibleImageUrls = computed(() => {
	if (
		["success", "error", "skipped", "stopped"].includes(
			completionStyle.value,
		)
	) {
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

async function handleDoubleClick(ev: MouseEvent) {
	if (
		component.value.type === "blueprints_code" ||
		component.value.type === "blueprints_setstate" ||
		component.value.type === "blueprints_returnvalue" ||
		component.value.type === "blueprints_logmessage"
	) {
		const isSelected = wfbm.isComponentIdSelected(componentId);
		if (isSelected) {
			// Expand the code editor
			wfbm.expandedEditorForComponent.value = componentId;
			tracking.track(
				isCodeComponent.value
					? "dbl_click_for_code_editor_opened"
					: "dbl_click_for_value_opened",
			);
		}
	} else if (component.value.type === "blueprints_runblueprint") {
		const bpKey = component.value.content?.blueprintKey ?? "";
		if (!bpKey) return;

		// Find the blueprint component by its key
		const blueprint = wf
			.getComponents("blueprints_root")
			.find((page) => page.content.key === bpKey);

		if (!blueprint) return;
		goToComponentParentPage(blueprint.id);
		await nextTick();
		wfbm.handleSelectionFromEvent(ev, blueprint.id, undefined, "tree");

		pushToast({
			type: "success",
			message: `Navigated to ${blueprint.content.key} blueprint`,
		});
		tracking.track("dbl_click_for_blueprint_navigated");
	}
}

function openLogs() {
	const item = latestKnownOutcomes.value.at(-1);
	if (!item) return;
	wfbm.openPanels.value.add("log");
	wfbm.setSelection(componentId, undefined, "click");
}

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

.BlueprintsNode--skipped {
	background: var(--wdsColorGray3) !important;
}

.BlueprintsNode--stopped {
	background: var(--wdsColorGray3) !important;
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

.BlueprintsNode__side {
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

.icon {
	pointer-events: none;
}

.BlueprintsNode__extraBorder {
	height: 100%;
	width: 100%;
	border-radius: 8px;
	overflow: hidden;
	position: absolute;
	top: 0;
	left: 0;
}

.BlueprintsNode:hover .BlueprintsNode__extraBorder {
	background-color: var(--wdsColorBlue2);
}

.BlueprintsNode--intelligent:hover .BlueprintsNode__extraBorder {
	background: var(
		--Gradients-Summer-Dawn-2,
		linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%)
	);
}

.BlueprintsNode.selected.component .BlueprintsNode__extraBorder {
	background: var(--wdsColorBlue4);
}

.BlueprintsNode__extraBorder .runner {
	height: 200%;
	width: 200%;
	position: absolute;
	top: -50%;
	left: -50%;
	background: conic-gradient(#6985ff, #f5f5f9);
	filter: blur(24px);
	animation: spin 1.5s linear infinite;
}

.BlueprintsNode--intelligent .BlueprintsNode__extraBorder .runner {
	background: conic-gradient(#6985ff, #ffd5f8, #bfcbff);
}

.BlueprintsNode__main {
	position: relative;
	margin: 2px;
	background: var(--builderBackgroundColor);
	border-radius: 6px;
}

.BlueprintsNode--intelligent .BlueprintsNode__main {
	margin-left: 8px;
	border-radius: 0 6px 6px 0;
}

.BlueprintsNode--trigger,
.BlueprintsNode--trigger .BlueprintsNode__main,
.BlueprintsNode--trigger .BlueprintsNode__extraBorder {
	border-radius: 36px;
}

.BlueprintsNode__main__title {
	display: grid;
	gap: 10px;
	border-radius: 12px 12px 0 0;
	align-items: center;
	grid-template-columns: 24px 1fr auto;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.BlueprintsNode--trigger .BlueprintsNode__main__title {
	border-bottom: unset;
}
.BlueprintsNode__main__title,
.BlueprintsNode__main__footer {
	padding: 12px;
}

.BlueprintsNode--intelligent .BlueprintsNode__main__title,
.BlueprintsNode--intelligent .BlueprintsNode__main__footer {
	padding-left: 6px;
}

.BlueprintsNode__main__title img {
	width: 24px;
	height: 24px;
}

.BlueprintsNode__main__title .deprecationNotice {
	font-size: 12px;
	text-transform: uppercase;
	font-size: 12px;
	font-weight: 500;
	line-height: 12px; /* 100% */
	letter-spacing: 1.3px;
	text-transform: uppercase;
	color: var(--builderSecondaryTextColor);
}

.BlueprintsNode--trigger .BlueprintsNode__main__title img {
	border-radius: 50%;
}

.BlueprintsNode:hover .nodeNamer :deep(.blockName) {
	background: var(--builderSubtleSeparatorColor);
}

.BlueprintsNode:hover .nodeNamer :deep(.aliasEditor) {
	background: var(--builderSubtleSeparatorColor);
}

.BlueprintsNode__main__outputs {
	border-radius: 0 0 12px 12px;
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 8px;
	padding-left: 6px;
	padding-top: 12px;
	padding-bottom: 12px;
	font-size: 12px;
}

.BlueprintsNode__main__outputs__title {
	grid-column: 1;
	color: var(--wdsColorGray4);
	text-transform: uppercase;
	font-weight: 500;
}
.BlueprintsNode__main__outputs__output {
	grid-column: 2;
	text-align: right;
}
.BlueprintsNode__main__outputs--float {
	position: absolute;
	right: 0;
	bottom: 48px;
	padding: 0;
	border-top: none;
}

.BlueprintsNode--trigger .BlueprintsNode__main__outputs {
	border: none;
	position: absolute;
	right: 0;
	top: 0;
	bottom: 0;
	padding: 0;
	height: 100%;
	justify-content: center;
}

.BlueprintsNode__main__footer {
	border-top: 1px solid var(--builderSeparatorColor);
	display: grid;
	grid-template-columns: 1fr auto;
}
.BlueprintsNode:has(.BlueprintsNode__main__outputs--float)
	.BlueprintsNode__main__footer {
	border-top: none;
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
