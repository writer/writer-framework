<template>
	<div class="BuilderJournal">
		<BuilderJournalHeader
			@refresh="loadEntries"
			@clear="deleteEntries"
			@download="downloadAsJson"
			@update:search="(val) => (searchText = val)"
			@update:statuses="(val) => (selectedStatuses = val)"
			@update:triggers="(val) => (selectedTriggers = val)"
		></BuilderJournalHeader>
		<div class="BuilderJournal__entries">
			<BuilderJournalEntry
				v-for="(entry, key) of sortedEntries"
				:key
				:journal-entry="entry"
			></BuilderJournalEntry>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ComputedRef, inject, onMounted, Ref, ref } from "vue";
import BuilderJournalHeader from "./journal/BuilderJournalHeader.vue";
import BuilderJournalEntry from "./journal/BuilderJournalEntry.vue";
import { convertAbsolutePathtoFullURL } from "@/utils/url";
import { useToasts } from "./useToast";
import { Component, WriterComponentDefinition } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";

const { pushToast } = useToasts();
const wf = inject(injectionKeys.core);

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
	component: Component;
	componentDefinition: WriterComponentDefinition;
};

const rawEntries: Ref<Record<string, RawJournalEntry>> = ref({});

const searchText = ref("");
const selectedStatuses = ref<string[]>([]);
const selectedTriggers = ref<string[]>([]);

const entries: ComputedRef<Record<string, JournalEntry>> = computed(() => {
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

			return [key, { ...entry, title, component, componentDefinition }];
		}),
	);
});

const filteredEntries: ComputedRef<Record<string, JournalEntry>> = computed(
	() => {
		return Object.fromEntries(
			Object.entries(entries.value).filter(([_, entry]) => {
				const searchMatch =
					searchText.value === "" ||
					entry.title
						.toLowerCase()
						.includes(searchText.value.toLowerCase());
				const statusMatch =
					selectedStatuses.value.length === 0 ||
					selectedStatuses.value.includes(entry.result);
				const triggerMatch =
					selectedTriggers.value.length === 0 ||
					selectedTriggers.value.includes(entry.trigger.type);
				return searchMatch && statusMatch && triggerMatch;
			}),
		);
	},
);

const sortedEntries: ComputedRef<Record<string, JournalEntry>> = computed(
	() => {
		const sortedArray = Object.entries(filteredEntries.value).sort(
			([_, a], [__, b]) =>
				new Date(b.timestamp).getTime() -
				new Date(a.timestamp).getTime(),
		);

		return Object.fromEntries(sortedArray);
	},
);

async function loadEntries() {
	const response = await fetch(
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

	if (!response.ok) {
		pushToast({
			type: "error",
			message: "Failed to fetch the execution history",
		});
		return;
	}

	const data = await response.json();

	rawEntries.value = { ...rawEntries.value, ...data.result };
}

const downloadAsJson = () => {
	const jsonString = JSON.stringify(filteredEntries.value, null, 2);
	const blob = new Blob([jsonString], { type: "application/json" });

	const a = document.createElement("a");
	a.href = URL.createObjectURL(blob);
	a.download = "agent-journal.json";

	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
};

async function deleteEntries() {
	const response = await fetch(
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

onMounted(() => {
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
