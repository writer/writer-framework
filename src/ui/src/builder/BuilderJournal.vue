<template>
	<div class="BuilderJournal">
		<BuilderJournalHeader
			v-model:filters="filters"
			@refresh="loadEntries"
			@clear="deleteEntries"
			@download="downloadAsJson"
		></BuilderJournalHeader>
		<div class="BuilderJournal__entries">
			<BuilderJournalEntry
				v-for="(entry, key) of sortedEntries"
				:key="key"
				:journal-entry="entry"
				@click="openEntryDetails(entry)"
			></BuilderJournalEntry>
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
			/>
		</WdsDrawer>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, onActivated, ref } from "vue";
import BuilderJournalHeader from "./journal/BuilderJournalHeader.vue";
import BuilderJournalEntry from "./journal/BuilderJournalEntry.vue";
import BuilderJournalEntryDetails from "./journal/BuilderJournalEntryDetails.vue";
import WdsDrawer from "@/wds/WdsDrawer.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { useToasts } from "./useToast";
import { Component, WriterComponentDefinition } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import type { JournalFilters } from "./journal/journalTypes";

defineOptions({
	name: "BuilderJournal",
});

const { pushToast } = useToasts();
const wf = inject(injectionKeys.core);
const builderManager = inject(injectionKeys.builderManager);

type ComponentInfo = {
	type: "blueprint" | "block";
	id: string;
};
type TriggerInfo = {
	type: "On demand" | "UI" | "API" | "Cron";
	event: string;
	component: ComponentInfo;
};

type BlockOutput = {
	result: any;
	outcome: string;
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

const filters = ref<JournalFilters>({
	search: "",
	statuses: [],
	triggers: [],
	instanceTypes: [],
});

const isDrawerOpen = ref(false);
const selectedEntry = ref<JournalEntry | null>(null);

const entries = computed<Record<string, JournalEntry>>(() => {
	return Object.fromEntries(
		Object.entries(rawEntries.value).map(([key, entry]) => {
			const component = wf.getComponentById(entry.trigger.component.id);
			const componentDefinition = wf.getComponentDefinition(
				component.type,
			);

			const title =
				component.type === "blueprints_blueprint"
					? component.content.key
					: component.content.alias || componentDefinition.name;

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

const filteredEntries = computed<Record<string, JournalEntry>>(() => {
	const searchTextLower = filters.value.search.toLowerCase();
	return Object.fromEntries(
		Object.entries(entries.value).filter(([_key, entry]) => {
			const searchMatch =
				filters.value.search === "" ||
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

const sortedEntries = computed<Record<string, JournalEntry>>(() => {
	const sortedArray = Object.entries(filteredEntries.value).sort(
		([_, a], [__, b]) =>
			new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
	);

	return Object.fromEntries(sortedArray);
});

async function loadEntries() {
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
		return;
	}

	if (!response.ok) {
		pushToast({
			type: "error",
			message: "Failed to fetch the execution history",
		});
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
	}
}

const downloadAsJson = () => {
	const rawFiltered = Object.fromEntries(
		Object.keys(filteredEntries.value).map((key) => {
			return [key, rawEntries.value[key]];
		}),
	);
	const jsonString = JSON.stringify(rawFiltered, null, 2);
	const blob = new Blob([jsonString], { type: "application/json" });

	const url = URL.createObjectURL(blob);
	try {
		const a = document.createElement("a");
		a.href = url;
		a.download = "agent-journal.json";
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	} finally {
		window.URL.revokeObjectURL(url);
	}
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
	isDrawerOpen.value = true;
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
	isDrawerOpen.value = false;

	// Switch to the appropriate mode based on trigger component type
	if (entry.trigger.component.type === "blueprint") {
		builderManager.mode.value = "blueprints";
	} else {
		builderManager.mode.value = "ui";
	}

	// Select the trigger component
	builderManager.setSelection(entry.trigger.component.id);

	pushToast({
		type: "success",
		message: `Jumped to ${entry.title}`,
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

.BuilderJournal__entries {
	overflow: auto;
	height: 100%;
}
</style>
