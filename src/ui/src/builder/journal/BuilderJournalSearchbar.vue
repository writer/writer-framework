<template>
	<div class="BuilderJournalSearchbar">
		<WdsTextInput v-model="searchText" left-icon="search" />
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsDropdownMenu
				:selected="statuses"
				:options="statusOptions"
				:enable-multi-selection="true"
				@select="onStatusesChange"
			></WdsDropdownMenu>
		</div>
		<div class="BuilderJournalSearchbar__dropdown">
			<WdsDropdownMenu
				:selected="triggers"
				:options="triggerOptions"
				:enable-multi-selection="true"
				@select="onTriggersChange"
			></WdsDropdownMenu>
		</div>
	</div>
</template>

<script setup lang="ts">
import WdsDropdownMenu from "@/wds/WdsDropdownMenu.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import { PropType } from "vue";

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
function onStatusesChange(val: string[]) {
	statuses.value = val;
}
function onTriggersChange(val: string[]) {
	triggers.value = val;
}
</script>

<style scoped>
.BuilderJournalSearchbar {
	width: fit-content;
	height: 100%;
	display: flex;
	flex-direction: row;
	gap: 8px;
}

.BuilderJournalSearchbar__dropdown {
	width: 250px;
	position: relative;
}
</style>
