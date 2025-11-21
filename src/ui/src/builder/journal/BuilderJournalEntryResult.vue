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
import { PropType } from "vue";

defineProps({
	result: {
		type: String as PropType<"success" | "error" | "stopped">,
		required: true,
	},
});
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
	background-color: var(--wdsColorGreen3);
}

.BuilderJournalEntryResult.error {
	background-color: var(--wdsColorOrange2);
}

.BuilderJournalEntryResult.stopped {
	background-color: var(--wdsColorGray1);
}

.BuilderJournalEntryResult__image {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 18px;
	height: 18px;
}
</style>
