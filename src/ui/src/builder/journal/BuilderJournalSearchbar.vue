<template>
	<div class="BuilderJournalSearchbar">
		<WdsTextInput v-model="filters.search" left-icon="search" />
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="filters.statuses"
				:options="STATUS_OPTIONS"
				:enable-multi-selection="true"
				placeholder="Status"
			/>
		</div>
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsSelect
				v-model="filters.triggers"
				:options="TRIGGER_OPTIONS"
				:enable-multi-selection="true"
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
	STATUS_OPTIONS,
	TRIGGER_OPTIONS,
	INSTANCE_TYPE_OPTIONS,
} from "./journalConstants";
import type { JournalFilters } from "./journalTypes";

const filters = defineModel("filters", { type: Object as PropType<JournalFilters>, required: true });

const hasActiveFilters = computed(() =>
	Object.values(filters.value).some((value) =>
		Array.isArray(value) ? value.length > 0 : Boolean(value),
	),
);

function clearAllFilters() {
	filters.value = {
		search: "",
		statuses: [],
		triggers: [],
		instanceTypes: [],
	};
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
	min-width: 200px;
	position: relative;
}
</style>
