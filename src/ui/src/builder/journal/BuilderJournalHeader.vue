<template>
	<div class="BuilderJournalHeader">
		<BuilderJournalSearchbar v-model:filters="filters">
		</BuilderJournalSearchbar>
		<div class="BuilderJournalHeader__actions">
			<WdsButton
				data-writer-tooltip="Refresh journal"
				data-writer-tooltip-placement="left"
				variant="neutral"
				size="smallIcon"
				@click="emit('refresh')"
			>
				<WdsIcon name="refresh-cw" />
			</WdsButton>
			<WdsButton
				data-writer-tooltip="Clear journal"
				data-writer-tooltip-placement="left"
				variant="neutral"
				size="smallIcon"
				@click="emit('clear')"
			>
				<WdsIcon name="trash-2" />
			</WdsButton>
			<WdsButton
				data-writer-tooltip="Download as JSON"
				data-writer-tooltip-placement="left"
				variant="neutral"
				size="smallIcon"
				@click="emit('download')"
			>
				<WdsIcon name="download" />
			</WdsButton>
		</div>
	</div>
</template>

<script setup lang="ts">
import WdsIcon from "@/wds/WdsIcon.vue";
import BuilderJournalSearchbar from "./BuilderJournalSearchbar.vue";
import WdsButton from "@/wds/WdsButton.vue";
import type { JournalFilters } from "./journalTypes";

const emit = defineEmits({
	refresh: () => true,
	clear: () => true,
	download: () => true,
});
const filters = defineModel<JournalFilters>("filters", { required: true });
</script>

<style scoped>
.BuilderJournalHeader {
	width: 100%;
	justify-content: space-between;
	padding: 16px 20px;
	display: flex;
	flex-direction: row;
	border-bottom: 1px solid var(--builderSeparatorColor);
	background: var(--wdsColorGray1);
}

.BuilderJournalHeader__actions {
	height: 100%;
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 8px;
}
</style>
