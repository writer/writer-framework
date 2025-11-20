<template>
	<div class="BuilderJournalSearchbar">
		<WdsTextInput v-model="searchText" left-icon="search" />
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="statuses"
				:options="statusOptions"
				:enable-multi-selection="true"
				placeholder="Status"
			/>
		</div>
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="triggers"
				:options="triggerOptions"
				:enable-multi-selection="true"
				placeholder="Trigger"
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

const statusOptions = [
	{ value: "success", label: "Success" },
	{ value: "error", label: "Error" },
	{ value: "stopped", label: "Stopped" },
];
const triggerOptions = [
	{ value: "On demand", label: "On demand" },
	{ value: "UI", label: "UI" },
	{ value: "API", label: "API" },
	{ value: "Cron", label: "Scheduled" },
];

const searchText = defineModel("search", { type: String });
const statuses = defineModel("statuses", { type: Array as PropType<string[]> });
const triggers = defineModel("triggers", { type: Array as PropType<string[]> });

const hasActiveFilters = computed(
	() => searchText.value || statuses.value?.length || triggers.value?.length,
);

function clearAllFilters() {
	searchText.value = "";
	statuses.value = [];
	triggers.value = [];
}
</script>

<style scoped>
.BuilderJournalSearchbar {
	width: fit-content;
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 8px;
}
.BuilderJournalSearchbar :deep(.WdsTextInput) {
	background: var(--wdsColorWhite);
	/* align with the height of the dropdown */
	max-height: 43px;
	height: 43px;
	max-width: 250px;
}
.BuilderJournalSearchbar__dropdown {
	min-width: 250px;
	position: relative;
}
</style>
