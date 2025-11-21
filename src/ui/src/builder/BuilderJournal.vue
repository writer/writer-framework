<template>
	<div class="BuilderJournal">
		<BuilderJournalHeader
			v-model:search="searchText"
			v-model:filters="filters"
			@refresh="loadEntries"
			@clear="deleteEntries"
			@download="downloadAsJson"
		/>
		<div v-if="loading" class="BuilderJournal__loading">
			<LoadingSymbol />
			<p>Loading entries...</p>
		</div>
		<div v-else class="BuilderJournal__entries">
			<BuilderJournalEntry
				v-for="(entry, key) of sortedEntries"
				:key="key"
				:journal-entry="entry"
				@click="openEntryDetails(entry)"
			/>
		</div>

		<!-- Drawer for entry details -->
		<WdsDrawer
			v-model="isDrawerOpen"
			title="Execution Details"
			size="large"
		>
			<BuilderJournalEntryDetails
				v-if="selectedEntry"
				:entry="selectedEntry"
				@re-run="handleReRun"
				@go-to-trigger="handleGoToTrigger"
				@go-to-block="handleGoToBlock"
			/>
		</WdsDrawer>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref, shallowRef, onActivated, onMounted } from "vue";
import BuilderJournalHeader from "./journal/BuilderJournalHeader.vue";
import BuilderJournalEntry from "./journal/BuilderJournalEntry.vue";
import BuilderJournalEntryDetails from "./journal/BuilderJournalEntryDetails.vue";
import WdsDrawer from "@/wds/WdsDrawer.vue";
import LoadingSymbol from "@/renderer/LoadingSymbol.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { downloadJson } from "@/utils/blob";
import { useToasts } from "./useToast";
import { Component, WriterComponentDefinition } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import type { JournalFilters } from "./journal/journalTypes";
import { useComponentActions } from "./useComponentActions";

defineOptions({
	name: "BuilderJournal",
});

const { pushToast } = useToasts();
const wf = inject(injectionKeys.core);
const builderManager = inject(injectionKeys.builderManager);

const { goToComponentParentPage, selectChild } = useComponentActions(
	wf,
	builderManager,
);

type ComponentInfo = {
	type: "blueprint" | "block";
	id: string;
	title: string;
};
type TriggerInfo = {
	type: "On demand" | "UI" | "API" | "Cron";
	event: string;
	component: ComponentInfo;
	payload: any;
};

type BlockOutput = {
	result: any;
	outcome: string;
	component?: ComponentInfo | null;
};

export type RawJournalEntry = {
	trigger: TriggerInfo;
	timestamp: string;
	blockOutputs: Record<string, BlockOutput>;
	instanceType: "editor" | "agent";
	result: "success" | "error" | "stopped";
};

export type JournalEntry = RawJournalEntry & {
	title: string;
	instanceTypeLabel: string;
	component: Component;
	componentDefinition: WriterComponentDefinition;
};

const rawEntries = ref<Record<string, RawJournalEntry>>({});
const loading = ref(false);

const searchText = ref("");
const filters = ref<JournalFilters>({
	statuses: [],
	triggers: [],
	instanceTypes: [],
});

const selectedEntry = shallowRef<JournalEntry | null>(null);
const isDrawerOpen = computed({
	get: () => !!selectedEntry.value,
	set: (value) => {
		if (!value) selectedEntry.value = null;
	},
});

const entries = computed<Record<string, JournalEntry | null>>(() => {
	return Object.fromEntries(
		Object.entries(rawEntries.value).map(([key, entry]) => {
			const component = wf.getComponentById(entry.trigger.component.id);
			if (!component) return [key, null];

			const componentDefinition = wf.getComponentDefinition(
				component?.type,
			);

			const title = component.content.key || componentDefinition.name;

			const instanceTypeLabel =
				entry.instanceType.charAt(0).toUpperCase() +
				entry.instanceType.slice(1);

			return [
				key,
				{
					...entry,
					title,
					instanceTypeLabel,
					component,
					componentDefinition,
				},
			];
		}),
	);
});

const filteredEntries = computed<Record<string, JournalEntry | null>>(() => {
	const searchTextLower = searchText.value.toLowerCase();
	return Object.fromEntries(
		Object.entries(entries.value).filter(([_key, entry]) => {
			if (!entry) return false;
			const searchMatch =
				searchText.value === "" ||
				entry.title.toLowerCase().includes(searchTextLower);
			const statusMatch =
				filters.value.statuses.length === 0 ||
				filters.value.statuses.includes(entry.result);
			const triggerMatch =
				filters.value.triggers.length === 0 ||
				filters.value.triggers.includes(entry.trigger.type);
			const instanceTypeMatch =
				filters.value.instanceTypes.length === 0 ||
				filters.value.instanceTypes.includes(entry.instanceType);
			return (
				searchMatch && statusMatch && triggerMatch && instanceTypeMatch
			);
		}),
	);
});

const sortedEntries = computed<Record<string, JournalEntry | null>>(() => {
	const sortedArray = Object.entries(filteredEntries.value)
		.filter(([_, entry]) => entry !== null)
		.sort(
			([_, a], [__, b]) =>
				new Date(b.timestamp).getTime() -
				new Date(a.timestamp).getTime(),
		);

	return Object.fromEntries(sortedArray);
});

async function loadEntries() {
	loading.value = true;
	let response: Response;
	try {
		response = await fetch(
			convertAbsolutePathtoFullURL("/api/data/retrieve"),
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					key_contains: "wf-journal-",
					skip_keys: Object.keys(rawEntries.value),
				}),
			},
		);
	} catch {
		pushToast({
			type: "error",
			message: "Failed to fetch the execution history",
		});
		loading.value = false;
		return;
	}

	if (!response.ok) {
		pushToast({
			type: "error",
			message: "Failed to fetch the execution history",
		});
		loading.value = false;
		return;
	}

	try {
		const data = await response.json();
		rawEntries.value = { ...rawEntries.value, ...data.result };
	} catch {
		pushToast({
			type: "error",
			message: "Failed to fetch the execution history",
		});
		return;
	} finally {
		loading.value = false;
	}
}

const downloadAsJson = () => {
	const rawFiltered = Object.fromEntries(
		Object.keys(filteredEntries.value).map((key) => {
			return [key, rawEntries.value[key]];
		}),
	);
	downloadJson(rawFiltered, "agent-journal.json");
};

async function deleteEntries() {
	let response: Response;
	try {
		response = await fetch(
			convertAbsolutePathtoFullURL("/api/data/delete"),
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					keys: Object.keys(filteredEntries.value),
				}),
			},
		);
	} catch {
		pushToast({
			type: "error",
			message: "Failed to delete the execution history",
		});
		return;
	}

	if (!response.ok) {
		pushToast({
			type: "error",
			message: "Failed to delete the execution history",
		});
		return;
	}

	const newRawEntries = { ...rawEntries.value };
	for (const key of Object.keys(filteredEntries.value)) {
		delete newRawEntries[key];
	}
	rawEntries.value = newRawEntries;
}

function openEntryDetails(entry: JournalEntry) {
	selectedEntry.value = entry;
}

function handleReRun(entry: JournalEntry) {
	// TODO: Implement re-run logic
	// This would trigger the same blueprint/workflow with the same inputs
	pushToast({
		type: "info",
		message: `Re-run functionality for ${entry.title} will be implemented soon`,
	});
	// Placeholder for re-run implementation
	// Will trigger the blueprint/workflow execution with entry data
}

function handleGoToTrigger(entry: JournalEntry) {
	// Close the drawer
	selectedEntry.value = null;

	// Go to the trigger component
	goToComponentParentPage(entry.trigger.component.id);
	selectChild(entry.trigger.component.id);
	pushToast({
		type: "success",
		message: `Jumped to ${entry.title}`,
	});
}

function handleGoToBlock(blockId: string) {
	// Close the drawer
	selectedEntry.value = null;

	// Go to the block component
	goToComponentParentPage(blockId);
	selectChild(blockId);
	pushToast({
		type: "success",
		message: "Jumped to block",
	});
}

onMounted(() => {
	loadEntries();
});

onActivated(() => {
	// Load new entries when returning to journal tab
	// This is efficient because loadEntries() uses skip_keys to avoid re-fetching existing entries
	loadEntries();
});
</script>

<style lang="css" scoped>
.BuilderJournal {
	display: flex;
	flex-direction: column;
	height: 100%;
}

.BuilderJournal__loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 16px;
	padding: 48px 20px;
	color: var(--wdsColorGray5);
	height: 100%;
}

.BuilderJournal__loading p {
	margin: 0;
	font-size: 14px;
}

.BuilderJournal__entries {
	overflow: auto;
	height: 100%;
}
</style>
