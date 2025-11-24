<template>
	<div class="BuilderJournalEntryDetails">
		<!-- Entry Header -->
		<div class="header">
			<div class="header__title">
				<h3>{{ entry.title }}</h3>
				<WdsTag :text="entry.result" :variant="statusVariant" />
			</div>
			<div class="header__meta">
				<span>{{ formattedDate }} {{ formattedTime }}</span>
				<span>{{ entry.instanceTypeLabel }}</span>
				<span>{{ entry.trigger.type }}</span>
			</div>
		</div>

		<!-- Actions Bar -->
		<div class="actions">
			<WdsButton
				variant="neutral"
				size="small"
				type="button"
				@click="reRunExecution"
			>
				<WdsIcon name="play" />
				Re-run
			</WdsButton>
			<WdsButton
				variant="neutral"
				size="small"
				type="button"
				@click="goToTrigger"
			>
				<WdsIcon name="locate" />
				Go to Trigger
			</WdsButton>
			<WdsButton
				variant="neutral"
				size="small"
				type="button"
				@click="downloadAsJson"
			>
				<WdsIcon name="download" />
				Download JSON
			</WdsButton>
			<SharedCopyClipboardButton
				:value="outputsJson"
				text="Copy Output"
				variant="neutral"
				size="small"
				label="Copy output to clipboard"
			/>
		</div>

		<!-- Tabs for different sections -->
		<div class="tabs-wrapper">
			<WdsTabs v-model="activeTab" :tabs="JOURNAL_TABS" variant="bar" />
		</div>

		<!-- Tab Content -->
		<div class="content">
			<!-- Outputs Tab -->
			<div v-if="activeTab === 'outputs'" class="outputs">
				<div
					v-for="([blockId, output], index) in blockOutputsArray"
					:key="blockId"
					class="output-block"
					:class="getOutcomeClass(output.outcome)"
				>
					<div
						class="output-block__header"
						role="button"
						tabindex="0"
						@click="goToBlock(blockId)"
						@keydown.enter="goToBlock(blockId)"
					>
						<div
							v-if="blockId"
							class="output-block__title-container"
						>
							<h4 class="output-block__title">
								{{
									output.component?.title ||
									`Block ${index + 1}`
								}}
							</h4>
							<div class="output-block__icon">
								<WdsIcon name="locate" />
							</div>
						</div>
						<h4 v-else>
							{{
								output.component?.title || `Block ${index + 1}`
							}}
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
							<span
								v-if="
									output.executionTimeInSeconds !== undefined
								"
							>
								Duration:
								{{
									formatDuration(
										output.executionTimeInSeconds,
									)
								}}
							</span>
						</div>
					</div>
					<SharedJsonViewer
						:data="output.result"
						is-root
						is-root-open
						enable-copy-to-json
					/>
				</div>
			</div>

			<!-- Metadata Tab -->
			<div v-if="activeTab === 'metadata'" class="metadata">
				<div class="metadata__section">
					<h4>Trigger Information</h4>
					<div class="metadata__row">
						<span class="label">Type:</span>
						<span>{{ entry.trigger.type }}</span>
					</div>
					<div class="metadata__row">
						<span class="label">Event:</span>
						<span>{{ entry.trigger.event }}</span>
					</div>
					<div class="metadata__row">
						<span class="label">Component ID:</span>
						<span>{{ entry.trigger.component.id }}</span>
					</div>
					<div class="metadata__row">
						<span class="label">Component Type:</span>
						<span>{{ entry.trigger.component.type }}</span>
					</div>
				</div>

				<div class="metadata__section">
					<h4>Execution Information</h4>
					<div class="metadata__row">
						<span class="label">Timestamp:</span>
						<span>{{ entry.timestamp }}</span>
					</div>
					<div class="metadata__row">
						<span class="label">Instance Type:</span>
						<span>{{ entry.instanceTypeLabel }}</span>
					</div>
					<div class="metadata__row">
						<span class="label">Result:</span>
						<span>{{ entry.result }}</span>
					</div>
				</div>
			</div>

			<!-- Raw JSON Tab -->
			<div v-if="activeTab === 'raw'" class="raw">
				<BuilderEmbeddedCodeEditor
					:model-value="rawJson"
					language="json"
					variant="full"
					disabled
				/>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import { JournalEntry } from "../BuilderJournal.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsTag from "@/wds/WdsTag.vue";
import WdsTabs from "@/wds/WdsTabs.vue";
import { JOURNAL_TABS } from "./journalConstants";
import SharedCopyClipboardButton from "@/components/shared/SharedCopyClipboardButton.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import { useDateTimeFormatter } from "@/composables/useDateTimeFormatter";
import { downloadJson } from "@/utils/blob";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { useToasts } from "../useToast";
import SharedJsonViewer from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BuilderEmbeddedCodeEditor = defineAsyncComponentWithLoader({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
});

const props = defineProps({
	entry: { type: Object as PropType<JournalEntry>, required: true },
});

const emit = defineEmits<{
	reRun: [entry: JournalEntry];
	goToTrigger: [entry: JournalEntry];
	goToBlock: [blockId: string];
}>();

const { pushToast } = useToasts();

const activeTab = ref<(typeof JOURNAL_TABS)[number]["value"]>("outputs");

const dateObj = computed(() => new Date(props.entry.timestamp));
const { formattedDate, formattedTime } = useDateTimeFormatter(dateObj, {
	dateOptions: { year: "numeric", month: "short", day: "numeric" },
	timeOptions: {
		hour: "numeric",
		minute: "2-digit",
		second: "2-digit",
		hour12: true,
	},
});

const statusVariant = computed(() => {
	const variants = {
		success: "success",
		error: "error",
		stopped: "warning",
	};
	return variants[props.entry.result] || "neutral";
});

const blockOutputsArray = computed(() => {
	const entries = Object.entries(props.entry.blockOutputs);
	// Sort by startedAt timestamp (earliest first, missing timestamps go to bottom)
	return entries.sort((a, b) => {
		const timeA = a[1].startedAt ?? Infinity;
		const timeB = b[1].startedAt ?? Infinity;
		return timeA - timeB;
	});
});

const rawJson = computed(() => JSON.stringify(props.entry, null, 2));

const outputsJson = computed(() =>
	JSON.stringify(props.entry.blockOutputs, null, 2),
);

function reRunExecution() {
	emit("reRun", props.entry);
	pushToast({ type: "info", message: "Re-running execution..." });
}

function goToTrigger() {
	emit("goToTrigger", props.entry);
}

function goToBlock(blockId: string | null) {
	if (!blockId) return;
	emit("goToBlock", blockId);
}

function downloadAsJson() {
	try {
		downloadJson(
			props.entry,
			`journal-entry-${props.entry.timestamp}.json`,
		);
		pushToast({ type: "success", message: "JSON file downloaded" });
	} catch (_error) {
		pushToast({ type: "error", message: "Failed to download file" });
	}
}

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
.BuilderJournalEntryDetails {
	display: flex;
	flex-direction: column;
	gap: 0;
	height: 100%;
}

.header {
	padding: 20px;
	background: var(--wdsColorGray1);
	border-bottom: 1px solid var(--wdsColorGray2);
}

.header__title {
	display: flex;
	align-items: center;
	gap: 12px;
}

.header__title h3 {
	margin: 0;
	font-size: 18px;
	font-weight: 600;
}

.header__meta {
	display: flex;
	gap: 16px;
	font-size: 14px;
	color: var(--wdsColorGray5);
	margin-top: 8px;
}

.actions {
	display: flex;
	gap: 8px;
	padding: 16px 20px;
	border-bottom: 1px solid var(--wdsColorGray2);
	background: var(--wdsColorWhite);
}

.tabs-wrapper {
	padding: 0;
	background: var(--wdsColorWhite);
	position: sticky;
	top: 0;
	z-index: 1;
}

.tabs-wrapper > .WdsTabs:first-child {
	padding: 0 20px;
}

.content {
	flex: 1;
	overflow-y: auto;
	background: var(--wdsColorWhite);
}

.outputs,
.metadata,
.raw {
	padding: 20px;
}

.output-block {
	border: 1px solid var(--wdsColorGray2);
	border-radius: 8px;
	padding: 16px;
	margin-bottom: 16px;
	background: var(--wdsColorGray1);
	transition: border-color 0.2s;
}
.output-block__title-container {
	display: flex;
	align-items: center;
	gap: 8px;
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
	background: var(--wdsColorRed1);
	border-color: var(--wdsColorRed2);
}

.output-block--error:hover {
	border-color: var(--wdsColorRed5);
}

.output-block--error:hover .output-block__title {
	color: var(--wdsColorRed6);
}

.output-block--error:hover .output-block__icon :deep(svg) {
	stroke: var(--wdsColorRed6);
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

.metadata__section {
	margin-bottom: 24px;
}

.metadata__section h4 {
	margin: 0 0 12px 0;
	font-size: 16px;
	font-weight: 600;
	color: var(--wdsColorBlack);
}

.metadata__row {
	display: flex;
	padding: 8px 0;
	border-bottom: 1px solid var(--wdsColorGray2);
}

.metadata__row:last-child {
	border-bottom: none;
}

.metadata__row .label {
	font-weight: 500;
	width: 180px;
	color: var(--wdsColorGray5);
}

.raw {
	height: calc(100vh - 300px);
	min-height: 400px;
}
</style>
