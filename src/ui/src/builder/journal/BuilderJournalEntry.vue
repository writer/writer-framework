<template>
	<div class="BuilderJournalEntry">
		<div class="BuilderJournalEntry__summary">
			<BuilderJournalEntryResult
				:result="journalEntry.result"
			></BuilderJournalEntryResult>
			<div class="BuilderJournalEntry__summary__component">
				{{ journalEntry.title }}
			</div>
		</div>
		<div class="BuilderJournalEntry__info">
			<div class="BuilderJournalEntry__info__datetime">
				<div>{{ formattedDate }}</div>
				<div class="BuilderJournalEntry__info__datetime__time">
					{{ formattedTime }}
				</div>
			</div>
			<div class="BuilderJournalEntry__info__details">
				{{ journalEntry.trigger.type }}
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import BuilderJournalEntryResult from "./BuilderJournalEntryResult.vue";
import { JournalEntry } from "../BuilderJournal.vue";

const props = defineProps<{
	journalEntry: JournalEntry;
}>();

const dateObj = new Date(props.journalEntry.timestamp);

const optionsDate: Intl.DateTimeFormatOptions = {
	year: "numeric",
	month: "short",
	day: "numeric",
};
const formattedDate = dateObj.toLocaleDateString(undefined, optionsDate);

const optionsTime: Intl.DateTimeFormatOptions = {
	hour: "numeric",
	minute: "2-digit",
	second: "2-digit",
	hour12: true,
};
const formattedTime = dateObj.toLocaleTimeString(undefined, optionsTime);
</script>

<style scoped>
.BuilderJournalEntry {
	width: 100%;
	height: fit-content;
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: space-between;
	padding: 12px 16px 12px 8px;
	border-bottom: 1px solid #e4e7ed;
}

.BuilderJournalEntry__summary {
	padding: 12px 0;
	width: fit-content;
	height: 100%;
	display: flex;
	flex-direction: row;
	gap: 12px;
}

.BuilderJournalEntry__summary__component {
	display: flex;
	align-items: center;
	justify-content: center;
}

.BuilderJournalEntry__info {
	width: fit-content;
	height: 100%;
	display: flex;
	flex-direction: column;
}

.BuilderJournalEntry__info__datetime {
	width: fit-content;
	height: 100%;
	display: flex;
	flex-direction: row;
	gap: 8px;
}

.BuilderJournalEntry__info__datetime__time {
	min-width: 72px;
}

.BuilderJournalEntry__info__details {
	color: var(--wdsColorGray4);
}
</style>
