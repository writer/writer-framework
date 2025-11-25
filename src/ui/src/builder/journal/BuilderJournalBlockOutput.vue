<template>
	<div class="output-block" :class="getOutcomeClass(output.outcome)">
		<div
			class="output-block__header"
			role="button"
			tabindex="0"
			@click="$emit('go-to-block', blockId)"
			@keydown.enter="$emit('go-to-block', blockId)"
		>
			<div v-if="blockId" class="output-block__title-container">
				<h4 class="output-block__title">
					{{ output.component?.title || `Block ${index + 1}` }}
				</h4>
				<div class="output-block__icon">
					<WdsIcon name="locate" />
				</div>
			</div>
			<h4 v-else>
				{{ output.component?.title || `Block ${index + 1}` }}
			</h4>
			<SharedImgWithFallback
				v-if="output.component?.type"
				class="output-block__type-icon"
				:alt="`${output.component.type} icon`"
				:urls="getComponentIconUrls(output.component?.type)"
				:loader-max-width-px="32"
				:loader-max-height-px="32"
			/>
		</div>
		<div class="output-block__meta">
			<div class="output-block__status">
				<span>Outcome: {{ output.outcome }}</span>
			</div>
			<div
				v-if="
					output.startedAt !== undefined ||
					output.executionTimeInSeconds !== undefined
				"
				class="output-block__timing"
			>
				<span v-if="output.startedAt !== undefined">
					Started: {{ formatTimestamp(output.startedAt) }}
				</span>
				<span v-if="output.executionTimeInSeconds !== undefined">
					Duration:
					{{ formatDuration(output.executionTimeInSeconds) }}
				</span>
			</div>
		</div>
		<!-- Block Output Tabs -->
		<div class="output-block__tabs">
			<WdsTabs
				:model-value="activeTab"
				:tabs="blockTabs"
				variant="bar"
				@update:model-value="(value) => (activeTab = value)"
			/>
		</div>

		<div class="output-block__tab-content">
			<!-- Error Details Tab -->
			<div
				v-if="output.message && activeTab === 'error'"
				class="output-block__message"
			>
				<div class="output-block__message-content">
					{{ output.message }}
				</div>
			</div>

			<!-- Stdout Tab -->
			<div
				v-if="output.stdout && activeTab === 'stdout'"
				class="output-block__log-section"
			>
				<pre class="output-block__log-content">{{ output.stdout }}</pre>
			</div>

			<!-- Logs Tab -->
			<div
				v-if="output.logs && activeTab === 'logs'"
				class="output-block__log-section"
			>
				<pre class="output-block__log-content">{{ output.logs }}</pre>
			</div>

			<!-- Result Tab -->
			<div
				v-if="activeTab === 'result'"
				class="output-block__result-section"
			>
				<SharedJsonViewer
					:data="output.result"
					is-root
					is-root-open
					enable-copy-to-json
				/>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType, ref, watch } from "vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsTabs from "@/wds/WdsTabs.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import SharedJsonViewer from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

type BlockOutput = {
	result: any;
	outcome: string;
	message?: string;
	stdout?: string;
	logs?: string;
	startedAt?: number;
	executionTimeInSeconds?: number;
	component?: {
		type?: string;
		title?: string;
	} | null;
};

const props = defineProps({
	blockId: { type: String, required: true },
	output: { type: Object as PropType<BlockOutput>, required: true },
	index: { type: Number, required: true },
});

defineEmits<{
	"go-to-block": [blockId: string];
}>();

const activeTab = ref<string>("");

// Build tabs based on available data
const blockTabs = computed(() => {
	const tabs = [];

	if (props.output.message) {
		tabs.push({ label: "Error", value: "error" });
	}
	if (props.output.stdout) {
		tabs.push({ label: "Stdout", value: "stdout" });
	}
	if (props.output.logs) {
		tabs.push({ label: "Logs", value: "logs" });
	}
	tabs.push({ label: "Result", value: "result" });

	return tabs;
});

watch(
	blockTabs,
	(tabs) => {
		if (!activeTab.value && tabs.length > 0) {
			activeTab.value = tabs[0].value;
		}
	},
	{ immediate: true },
);

function formatTimestamp(timestamp: number): string {
	const date = new Date(timestamp * 1000);
	return date.toLocaleTimeString("en-US", {
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
		hour12: true,
	});
}

function formatDuration(seconds: number): string {
	if (seconds < 1) {
		return `${(seconds * 1000).toFixed(0)}ms`;
	}
	return `${seconds.toFixed(2)}s`;
}

function getOutcomeClass(outcome: string): string {
	const outcomeMap: Record<string, string> = {
		success: "output-block--success",
		trigger: "output-block--trigger",
		skipped: "output-block--skipped",
		error: "output-block--error",
		stopped: "output-block--skipped",
	};
	return outcomeMap[outcome] || "output-block--success";
}

function getComponentIconUrls(componentType: string | undefined): string[] {
	if (!componentType) return [];
	return [
		`/components/${componentType}.svg`,
		`/components/category_Blocks.svg`,
	].map((p) => convertAbsolutePathtoFullURL(p));
}
</script>

<style scoped>
.output-block {
	border: 1px solid var(--wdsColorGray3);
	border-radius: 6px;
	padding: 16px;
	margin-bottom: 16px;
	background: var(--wdsColorGray1);
	transition: border-color 0.2s;
}

.output-block__type-icon {
	width: 32px;
	height: 32px;
	flex-shrink: 0;
}

.output-block__type-icon img {
	width: 100%;
	height: 100%;
	object-fit: contain;
}

.output-block__header {
	margin-bottom: 8px;
	cursor: pointer;
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 8px;
}

.output-block__title-container {
	display: flex;
	align-items: center;
	gap: 8px;
}

.output-block__title {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
	color: var(--wdsColorBlack);
	display: inline-flex;
	align-items: center;
	gap: 8px;
	transition: color 0.2s;
}

.output-block__icon {
	opacity: 0;
	visibility: hidden;
	width: 16px;
	height: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition:
		opacity 0.2s,
		visibility 0.2s;
}

.output-block__icon :deep(svg) {
	width: 16px;
	height: 16px;
	transition: stroke 0.2s;
}

.output-block:hover .output-block__icon {
	opacity: 1;
	visibility: visible;
}

.output-block h4 {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
}

.output-block__meta {
	margin: 8px 0;
	display: flex;
	flex-direction: column;
	gap: 4px;
	font-size: 14px;
	color: var(--wdsColorGray5);
}

.output-block__status {
	display: flex;
	align-items: center;
}

.output-block__timing {
	display: flex;
	gap: 16px;
	font-size: 13px;
}

.output-block__message-content {
	padding: 12px;
	background: var(--wdsColorGray0);
	border: 1px solid var(--wdsColorGray3);
	border-radius: 4px;
	font-size: 13px;
	overflow-x: auto;
	color: var(--wdsColorGray7);
}

.output-block__message-content :deep(pre) {
	margin: 0;
	font-family: "Courier New", Courier, monospace;
	font-size: 12px;
	font-weight: 600;
	white-space: pre-wrap;
	word-break: break-word;
}

/* Outcome-based color variants */
.output-block--success {
	background: var(--wdsColorGreen1);
	border-color: var(--wdsColorGreen5);
}

.output-block--success:hover {
	border-color: var(--wdsColorGreen6);
}

.output-block--success:hover .output-block__title {
	color: var(--wdsColorGreen6);
}

.output-block--success:hover .output-block__icon :deep(svg) {
	stroke: var(--wdsColorGreen6);
}

.output-block--trigger {
	background: var(--wdsColorBlue1);
	border-color: var(--wdsColorBlue2);
}

.output-block--trigger:hover {
	border-color: var(--wdsColorBlue5);
}

.output-block--trigger:hover .output-block__title {
	color: var(--wdsColorBlue6);
}

.output-block--trigger:hover .output-block__icon :deep(svg) {
	stroke: var(--wdsColorBlue6);
}

.output-block--error {
	background: var(--wdsColorOrange1);
	border-color: var(--wdsColorOrange2);
}

.output-block--error:hover {
	border-color: var(--wdsColorOrange5);
}

.output-block--error:hover .output-block__title {
	color: var(--wdsColorOrange5);
}

.output-block--error:hover .output-block__icon :deep(svg) {
	stroke: var(--wdsColorOrange5);
}

.output-block--skipped {
	background: var(--wdsColorGray1);
	border-color: var(--wdsColorGray2);
}

.output-block--skipped:hover {
	border-color: var(--wdsColorGray4);
}

.output-block--skipped:hover .output-block__title {
	color: var(--wdsColorGray6);
}

.output-block--skipped:hover .output-block__icon :deep(svg) {
	stroke: var(--wdsColorGray6);
}

/* Block tabs */
.output-block__tabs {
	margin: 12px 0 0 0;
	border-top: 1px solid var(--wdsColorGray2);
	padding-top: 8px;
}

.output-block__tab-content {
	margin-top: 12px;
}

.output-block__tab-content .output-block__log-section,
.output-block__tab-content .output-block__result-section,
.output-block__tab-content .output-block__message {
	margin: 0;
}

.output-block__log-section {
	margin: 12px 0;
}

.output-block__log-content {
	margin: 0;
	padding: 12px;
	background: var(--wdsColorGray0);
	border: 1px solid var(--wdsColorGray3);
	border-radius: 4px;
	font-family: "Courier New", Courier, monospace;
	font-size: 12px;
	font-weight: 500;
	white-space: pre-wrap;
	word-break: break-word;
	color: var(--wdsColorGray7);
	overflow-x: auto;
	max-height: 400px;
	overflow-y: auto;
}

.output-block__result-section {
	margin: 12px 0;
}

.output-block__result-section :deep(.SharedControlBar__content) {
	margin: 0;
	padding: 12px;
	width: 100%;
	background: var(--wdsColorGray0);
	border: 1px solid var(--wdsColorGray3);
	border-radius: 4px;
	font-family: "Courier New", Courier, monospace;
	font-size: 12px;
	font-weight: 500;
}

.output-block__result-section :deep(.SharedControlBar) {
	align-items: center;
}
</style>
