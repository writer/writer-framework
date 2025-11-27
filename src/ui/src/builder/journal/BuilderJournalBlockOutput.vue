<template>
	<div class="BuilderJournalBlockOutput" :class="rootClass">
		<div
			class="BuilderJournalBlockOutput__header"
			:role="blockId ? 'button' : undefined"
			:tabindex="blockId ? '0' : undefined"
			@click="blockId && $emit('go-to-block', blockId)"
			@keydown.enter="blockId && $emit('go-to-block', blockId)"
		>
			<div
				v-if="blockId"
				class="BuilderJournalBlockOutput__title-container"
			>
				<h4 class="BuilderJournalBlockOutput__title">
					{{ output.component?.title || `Block ${index + 1}` }}
				</h4>
				<div class="BuilderJournalBlockOutput__icon">
					<WdsIcon name="locate" />
				</div>
			</div>
			<h4 v-else>
				{{ output.component?.title || `Block ${index + 1}` }}
			</h4>
			<SharedImgWithFallback
				v-if="output.component?.type"
				class="BuilderJournalBlockOutput__type-icon"
				:alt="`${output.component.type} icon`"
				:urls="
					getComponentIconUrls(
						output.component?.type,
						output.component?.category,
					)
				"
				:loader-max-width-px="32"
				:loader-max-height-px="32"
			/>
		</div>
		<div class="BuilderJournalBlockOutput__meta">
			<div class="BuilderJournalBlockOutput__status">
				<span>Outcome: {{ output.outcome }}</span>
			</div>
			<div
				v-if="
					output.startedAt !== undefined ||
					output.executionTimeInSeconds !== undefined
				"
				class="BuilderJournalBlockOutput__timing"
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
		<div class="BuilderJournalBlockOutput__tabs">
			<WdsTabs
				:model-value="activeTab"
				:tabs="blockTabs"
				variant="bar"
				@update:model-value="(value) => (activeTab = value)"
			/>
		</div>

		<div class="BuilderJournalBlockOutput__tab-content">
			<!-- Error Details Tab -->
			<div
				v-if="output.message && activeTab === 'error'"
				class="BuilderJournalBlockOutput__message"
			>
				<div class="BuilderJournalBlockOutput__message-content">
					{{ output.message }}
				</div>
			</div>

			<!-- Stdout Tab -->
			<div
				v-if="output.stdout && activeTab === 'stdout'"
				class="BuilderJournalBlockOutput__log-section"
			>
				<pre class="BuilderJournalBlockOutput__log-content">{{
					output.stdout
				}}</pre>
			</div>

			<!-- Logs Tab -->
			<div
				v-if="output.logs && activeTab === 'logs'"
				class="BuilderJournalBlockOutput__log-section"
			>
				<pre class="BuilderJournalBlockOutput__log-content">{{
					output.logs
				}}</pre>
			</div>

			<!-- Result Tab -->
			<div
				v-if="activeTab === 'result'"
				class="BuilderJournalBlockOutput__result-section"
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
	result: unknown;
	outcome: string;
	message?: string;
	stdout?: string;
	logs?: string;
	startedAt?: number;
	executionTimeInSeconds?: number;
	component?: {
		type?: string;
		title?: string;
		category?: string;
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
		if (!tabs.length) {
			activeTab.value = "";
			return;
		}
		if (!tabs.some((tab) => tab.value === activeTab.value)) {
			activeTab.value = tabs[0].value;
		}
	},
	{ immediate: true },
);

function formatTimestamp(timestamp: number): string {
	const date = new Date(timestamp * 1000);
	return date.toLocaleTimeString(undefined, {
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

const rootClassByOutcome: Record<string, string> = {
	success: "BuilderJournalBlockOutput--success",
	trigger: "BuilderJournalBlockOutput--trigger",
	skipped: "BuilderJournalBlockOutput--skipped",
	error: "BuilderJournalBlockOutput--error",
	stopped: "BuilderJournalBlockOutput--skipped",
};

const rootClass = computed(
	() =>
		rootClassByOutcome[props.output.outcome] ||
		"BuilderJournalBlockOutput--success",
);

function getComponentIconUrls(
	componentType: string | undefined,
	componentCategory: string | undefined,
): string[] {
	const paths = [
		`/components/${componentType}.svg`,
		`/components/blueprints_category_${componentCategory}.svg`,
		`/components/category_Blocks.svg`,
	];

	//TODO: Add custom block icons

	return paths.map((p) => convertAbsolutePathtoFullURL(p));
}
</script>

<style scoped>
.BuilderJournalBlockOutput {
	border: 1px solid var(--wdsColorGray3);
	border-radius: 6px;
	padding: 16px;
	margin-bottom: 16px;
	background: var(--wdsColorGray1);
	transition: border-color 0.2s;
}

.BuilderJournalBlockOutput__type-icon {
	width: 32px;
	height: 32px;
	flex-shrink: 0;
}

.BuilderJournalBlockOutput__type-icon img {
	width: 100%;
	height: 100%;
	object-fit: contain;
}

.BuilderJournalBlockOutput__header {
	margin-bottom: 8px;
	cursor: pointer;
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 8px;
}

.BuilderJournalBlockOutput__title-container {
	display: flex;
	align-items: center;
	gap: 8px;
}

.BuilderJournalBlockOutput__title {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
	color: var(--wdsColorBlack);
	display: inline-flex;
	align-items: center;
	gap: 8px;
	transition: color 0.2s;
}

.BuilderJournalBlockOutput__icon {
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

.BuilderJournalBlockOutput__icon :deep(svg) {
	width: 16px;
	height: 16px;
	transition: stroke 0.2s;
}

.BuilderJournalBlockOutput:hover .BuilderJournalBlockOutput__icon {
	opacity: 1;
	visibility: visible;
}

.BuilderJournalBlockOutput h4 {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
}

.BuilderJournalBlockOutput__meta {
	margin: 8px 0;
	display: flex;
	flex-direction: column;
	gap: 4px;
	font-size: 14px;
	color: var(--wdsColorGray5);
}

.BuilderJournalBlockOutput__status {
	display: flex;
	align-items: center;
}

.BuilderJournalBlockOutput__timing {
	display: flex;
	gap: 16px;
	font-size: 13px;
}

.BuilderJournalBlockOutput__message-content {
	padding: 12px;
	background: var(--wdsColorGray0);
	border: 1px solid var(--wdsColorGray3);
	border-radius: 4px;
	font-size: 13px;
	overflow-x: auto;
	color: var(--wdsColorGray7);
}

.BuilderJournalBlockOutput__message-content :deep(pre) {
	margin: 0;
	font-family: "Courier New", Courier, monospace;
	font-size: 12px;
	font-weight: 600;
	white-space: pre-wrap;
	word-break: break-word;
}

/* Outcome-based color variants */
.BuilderJournalBlockOutput--success {
	background: var(--wdsColorGreen1);
	border-color: var(--wdsColorGreen5);
}

.BuilderJournalBlockOutput--success:hover {
	border-color: var(--wdsColorGreen6);
}

.BuilderJournalBlockOutput--success:hover .BuilderJournalBlockOutput__title {
	color: var(--wdsColorGreen6);
}

.BuilderJournalBlockOutput--success:hover
	.BuilderJournalBlockOutput__icon
	:deep(svg) {
	stroke: var(--wdsColorGreen6);
}

.BuilderJournalBlockOutput--trigger {
	background: var(--wdsColorBlue1);
	border-color: var(--wdsColorBlue2);
}

.BuilderJournalBlockOutput--trigger:hover {
	border-color: var(--wdsColorBlue5);
}

.BuilderJournalBlockOutput--trigger:hover .BuilderJournalBlockOutput__title {
	color: var(--wdsColorBlue6);
}

.BuilderJournalBlockOutput--trigger:hover
	.BuilderJournalBlockOutput__icon
	:deep(svg) {
	stroke: var(--wdsColorBlue6);
}

.BuilderJournalBlockOutput--error {
	background: var(--wdsColorOrange1);
	border-color: var(--wdsColorOrange2);
}

.BuilderJournalBlockOutput--error:hover {
	border-color: var(--wdsColorOrange5);
}

.BuilderJournalBlockOutput--error:hover .BuilderJournalBlockOutput__title {
	color: var(--wdsColorOrange5);
}

.BuilderJournalBlockOutput--error:hover
	.BuilderJournalBlockOutput__icon
	:deep(svg) {
	stroke: var(--wdsColorOrange5);
}

.BuilderJournalBlockOutput--skipped {
	background: var(--wdsColorGray1);
	border-color: var(--wdsColorGray2);
}

.BuilderJournalBlockOutput--skipped:hover {
	border-color: var(--wdsColorGray4);
}

.BuilderJournalBlockOutput--skipped:hover .BuilderJournalBlockOutput__title {
	color: var(--wdsColorGray6);
}

.BuilderJournalBlockOutput--skipped:hover
	.BuilderJournalBlockOutput__icon
	:deep(svg) {
	stroke: var(--wdsColorGray6);
}

/* Block tabs */
.BuilderJournalBlockOutput__tabs {
	margin: 12px 0 0 0;
	border-top: 1px solid var(--wdsColorGray2);
	padding-top: 8px;
}

.BuilderJournalBlockOutput__tab-content {
	margin-top: 12px;
}

.BuilderJournalBlockOutput__tab-content .BuilderJournalBlockOutput__log-section,
.BuilderJournalBlockOutput__tab-content
	.BuilderJournalBlockOutput__result-section,
.BuilderJournalBlockOutput__tab-content .BuilderJournalBlockOutput__message {
	margin: 0;
}

.BuilderJournalBlockOutput__log-section {
	margin: 12px 0;
}

.BuilderJournalBlockOutput__log-content {
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

.BuilderJournalBlockOutput__result-section {
	margin: 12px 0;
}

.BuilderJournalBlockOutput__result-section :deep(.SharedControlBar__content) {
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

.BuilderJournalBlockOutput__result-section :deep(.SharedControlBar) {
	align-items: center;
}
</style>
