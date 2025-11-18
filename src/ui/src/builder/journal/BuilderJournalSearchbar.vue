<template>
	<div class="BuilderJournalSearchbar">
		<WdsTextInput
			v-model="searchText"
			class="searchInput"
			left-icon="search"
			@input="onSearchChange"
		/>
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
import { Ref, ref } from "vue";

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

const searchText = ref("");
const statuses: Ref<string[]> = ref([]);
const triggers: Ref<string[]> = ref([]);

const emit = defineEmits<{
	(e: "update:search", value: string): void;
	(e: "update:statuses", value: string[]): void;
	(e: "update:triggers", value: string[]): void;
}>();

function onSearchChange() {
	emit("update:search", searchText.value);
}

function onStatusesChange(val: string[]) {
	statuses.value = val;
	emit("update:statuses", val);
}

function onTriggersChange(val: string[]) {
	triggers.value = val;
	emit("update:triggers", val);
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
.BuilderJournalSearchbar__search {
	width: fit-content;
	height: 100%;
}
.BuilderJournalSearchbar__dropdown {
	width: 250px;
	position: relative;
}
</style>
