<template>
	<div class="BuilderJournalEntryResult" :class="result">
		<div class="BuilderJournalEntryResult__image">
			<WdsIcon v-if="result === 'success'" name="check" />
			<WdsIcon v-else-if="result === 'error'" name="triangle-alert" />
			<WdsIcon v-else-if="result === 'stopped'" name="octagon-pause" />
		</div>
	</div>
</template>

<script setup lang="ts">
import WdsIcon from "@/wds/WdsIcon.vue";

defineProps<{
	result: "success" | "error" | "stopped";
}>();
</script>

<style scoped>
.BuilderJournalEntryResult {
	height: 24px;
	width: 24px;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.BuilderJournalEntryResult.success {
	background-color: #a9f9e1;
}

.BuilderJournalEntryResult.error {
	background-color: #ffcfc2;
}

.BuilderJournalEntryResult.stopped {
	background-color: #f5f5f9;
}

.BuilderJournalEntryResult__image {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 18px;
	height: 18px;
}
</style>
