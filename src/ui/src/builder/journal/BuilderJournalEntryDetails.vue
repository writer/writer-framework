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
				>
					<h4>Block {{ index + 1 }}</h4>
					<div class="output-block__status">
						<span>Outcome: {{ output.outcome }}</span>
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
import { useDateTimeFormatter } from "@/composables/useDateTimeFormatter";
import { downloadJson } from "@/utils/blob";
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

const blockOutputsArray = computed(() =>
	Object.entries(props.entry.blockOutputs),
);

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
}

.output-block h4 {
	margin: 0 0 8px 0;
	font-size: 16px;
	font-weight: 600;
}

.output-block__status {
	margin: 8px 0;
	font-size: 14px;
	color: var(--wdsColorGray5);
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
