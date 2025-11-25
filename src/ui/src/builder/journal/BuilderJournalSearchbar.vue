<template>
	<div class="BuilderJournalSearchbar">
		<WdsTextInput v-model="search" left-icon="search" />
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="filters.statuses"
				:options="STATUS_OPTIONS"
				enable-multi-selection
				placeholder="Status"
			/>
		</div>
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="filters.triggers"
				:options="TRIGGER_OPTIONS"
				enable-multi-selection
				placeholder="Trigger"
			/>
		</div>
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="filters.instanceTypes"
				:options="INSTANCE_TYPE_OPTIONS"
				enable-multi-selection
				placeholder="Instance Type"
			/>
		</div>
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="filters.entryTypes"
				:options="ENTRY_TYPE_OPTIONS"
				enable-multi-selection
				placeholder="Entry Type"
			/>
		</div>
		<WdsButton
			v-if="hasActiveFilters"
			data-writer-tooltip="Clear filters"
			data-writer-tooltip-placement="bottom"
			variant="neutral"
			@click="clearAllFilters"
		>
			Clear
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import WdsSelect from "@/wds/WdsSelect.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { computed, PropType } from "vue";
import {
	ENTRY_TYPE_OPTIONS,
	INSTANCE_TYPE_OPTIONS,
	STATUS_OPTIONS,
	TRIGGER_OPTIONS,
} from "./journalConstants";
import type { JournalFilters } from "./journalTypes";

// Separate models for search and filters
const search = defineModel<string>("search", {
	type: String,
	required: true,
});
const filters = defineModel<JournalFilters>("filters", {
	type: Object as PropType<JournalFilters>,
	required: true,
});

const hasActiveFilters = computed(
	() =>
		Boolean(search.value) ||
		filters.value.statuses.length > 0 ||
		filters.value.triggers.length > 0 ||
		filters.value.instanceTypes.length > 0 ||
		filters.value.entryTypes.length > 0,
);

function clearAllFilters() {
	search.value = "";
	filters.value = {
		statuses: [],
		triggers: [],
		instanceTypes: [],
		entryTypes: [],
	};
}
</script>

<style scoped>
.BuilderJournalSearchbar {
	width: fit-content;
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
	align-items: center;
	gap: 8px;
}
.BuilderJournalSearchbar :deep(.WdsTextInput) {
	background: var(--wdsColorWhite);
	/* align with the height of the dropdown */
	max-height: 43px;
	height: 43px;

	width: 200px;
}
.BuilderJournalSearchbar__dropdown {
	min-width: 200px;
	position: relative;
}
</style>
