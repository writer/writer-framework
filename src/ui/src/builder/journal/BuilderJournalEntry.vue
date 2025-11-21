<template>
	<div class="BuilderJournalEntry">
		<div class="BuilderJournalEntry__summary">
			<BuilderJournalEntryResult
				:result="journalEntry.result"
			></BuilderJournalEntryResult>
			<div class="BuilderJournalEntry__summary__content">
				<div class="BuilderJournalEntry__summary__component">
					{{ journalEntry.title }}
				</div>
				<div class="BuilderJournalEntry__summary__instanceType">
					{{ journalEntry.instanceTypeLabel }}
				</div>
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
import { computed, PropType } from "vue";
import { useDateTimeFormatter } from "@/composables/useDateTimeFormatter";

const props = defineProps({
	journalEntry: { type: Object as PropType<JournalEntry>, required: true },
});

const dateObj = computed(() => new Date(props.journalEntry.timestamp));

const { formattedDate, formattedTime } = useDateTimeFormatter(dateObj, {
	dateOptions: {
		year: "numeric",
		month: "short",
		day: "numeric",
	},
	timeOptions: {
		hour: "numeric",
		minute: "2-digit",
		second: "2-digit",
		hour12: true,
	},
});
</script>

<style scoped>
.BuilderJournalEntry {
	width: 100%;
	height: fit-content;
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: space-between;
	padding: 12px 20px;
	border-bottom: 1px solid #e4e7ed;
}

.BuilderJournalEntry__summary {
	padding: 12px 0;
	width: fit-content;
	height: 100%;
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 12px;
}

.BuilderJournalEntry__summary__content {
	display: flex;
	flex-direction: column;
	gap: 0px;
	justify-content: center;
}

.BuilderJournalEntry__summary__component {
	font-weight: 500;
}

.BuilderJournalEntry__summary__instanceType {
	font-size: 12px;
	color: var(--wdsColorGray5);
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
