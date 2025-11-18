<template>
	<div class="BuilderJournalHeader">
		<BuilderJournalSearchbar
			@update:search="(val) => emit('update:search', val)"
			@update:statuses="(val) => emit('update:statuses', val)"
			@update:triggers="(val) => emit('update:triggers', val)"
		>
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

const emit = defineEmits<{
	(e: "refresh"): void;
	(e: "clear"): void;
	(e: "download"): void;
	(e: "update:search", value: string): void;
	(e: "update:statuses", value: string[]): void;
	(e: "update:triggers", value: string[]): void;
}>();
</script>

<style scoped>
.BuilderJournalHeader {
	width: 100%;
	height: 72px;
	justify-content: space-between;
	padding: 16px;
	display: flex;
	flex-direction: row;
}

.BuilderJournalHeader__actions {
	width: fit-content;
	height: 100%;
	display: flex;
	flex-direction: row;
	gap: 8px;
}
</style>
