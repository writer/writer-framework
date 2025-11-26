<template>
	<div class="BuilderJournalEntryDetails">
		<!-- Entry Header -->
		<BuilderJournalEntryHeader :entry="entry" />

		<!-- Actions Bar -->
		<BuilderJournalEntryActions
			:entry="entry"
			@re-run="reRunExecution"
			@go-to-trigger="goToTrigger"
			@download="downloadAsJson"
		/>

		<!-- Tabs for different sections -->
		<div class="tabs-wrapper">
			<WdsTabs v-model="activeTab" :tabs="JOURNAL_TABS" variant="bar" />
		</div>

		<!-- Tab Content -->
		<div class="content">
			<!-- Outputs Tab -->
			<div v-if="activeTab === 'outputs'" class="outputs">
				<!-- Init Logs Outputs -->
				<BuilderJournalInitLogOutput
					v-if="entry.entryType === 'init'"
					:entry="entry"
				/>

				<!-- Execution Block Outputs -->
				<template v-else>
					<BuilderJournalBlockOutput
						v-for="([blockId, output], index) in blockOutputsArray"
						:key="blockId"
						:block-id="blockId"
						:output="output"
						:index="index"
						@go-to-block="goToBlock"
					/>
				</template>
			</div>

			<!-- Metadata Tab -->
			<BuilderJournalMetadata
				v-if="activeTab === 'metadata'"
				:entry="entry"
			/>

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
import { computed, type PropType, ref } from "vue";
import type { UnifiedEntry } from "../BuilderJournal.vue";
import WdsTabs from "@/wds/WdsTabs.vue";
import { JOURNAL_TABS } from "./journalConstants";
import BuilderJournalEntryHeader from "./BuilderJournalEntryHeader.vue";
import BuilderJournalEntryActions from "./BuilderJournalEntryActions.vue";
import BuilderJournalBlockOutput from "./BuilderJournalBlockOutput.vue";
import BuilderJournalInitLogOutput from "./BuilderJournalInitLogOutput.vue";
import BuilderJournalMetadata from "./BuilderJournalMetadata.vue";
import { downloadJson } from "@/utils/blob";
import { useToasts } from "../useToast";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BuilderEmbeddedCodeEditor = defineAsyncComponentWithLoader({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
});

const props = defineProps({
	entry: { type: Object as PropType<UnifiedEntry>, required: true },
});

const emit = defineEmits<{
	reRun: [entry: UnifiedEntry];
	goToTrigger: [entry: UnifiedEntry];
	goToBlock: [blockId: string];
}>();

const { pushToast } = useToasts();

const activeTab = ref<(typeof JOURNAL_TABS)[number]["value"]>("outputs");

const blockOutputsArray = computed(() => {
	if (props.entry.entryType !== "execution") return [];
	const entries = Object.entries(props.entry.blockOutputs);
	// Sort by startedAt timestamp (earliest first, missing timestamps go to bottom)
	return entries.sort((a, b) => {
		const timeA = a[1].startedAt ?? Infinity;
		const timeB = b[1].startedAt ?? Infinity;
		return timeA - timeB;
	});
});

const rawJson = computed(() => JSON.stringify(props.entry, null, 2));

function reRunExecution() {
	emit("reRun", props.entry);
}

function goToTrigger() {
	emit("goToTrigger", props.entry);
}

function goToBlock(blockId: string) {
	emit("goToBlock", blockId);
}

function downloadAsJson() {
	try {
		downloadJson(
			props.entry,
			`journal-entry-${props.entry.timestamp}.json`,
		);
	} catch {
		pushToast({ type: "error", message: "Failed to download file" });
	}
}
</script>

<style scoped>
.BuilderJournalEntryDetails {
	display: flex;
	flex-direction: column;
	height: 100%;
	background: var(--wdsColorWhite);
}

.tabs-wrapper {
	padding: 0 20px;
	border-bottom: 1px solid var(--wdsColorGray2);
}

.content {
	flex: 1;
	overflow-y: auto;
}

.outputs {
	padding: 20px;
}

.raw {
	height: 100%;
	display: flex;
	flex-direction: column;
}
</style>
