<template>
	<div class="header">
		<div class="header__title">
			<h3>{{ entry.title }}</h3>
			<WdsTag
				v-if="entry.entryType === 'execution'"
				:text="entry.result.toUpperCase()"
				:variant="statusVariant"
			/>
			<WdsTag v-else text="INIT" variant="neutral" />
		</div>
		<div class="header__meta">
			<span>{{ formattedDate }} {{ formattedTime }}</span>
			<span>{{ entry.instanceTypeLabel }}</span>
			<span v-if="entry.entryType === 'execution'">{{
				entry.trigger.type
			}}</span>
			<span v-else>{{ entry.mode }}</span>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";
import WdsTag from "@/wds/WdsTag.vue";
import { useDateTimeFormatter } from "@/composables/useDateTimeFormatter";
import type { UnifiedEntry } from "../BuilderJournal.vue";

const props = defineProps({
	entry: { type: Object as PropType<UnifiedEntry>, required: true },
});

const dateObj = computed(() => new Date(props.entry.timestamp));
const { formattedDate, formattedTime } = useDateTimeFormatter(dateObj, {
	dateOptions: { year: "numeric", month: "short", day: "numeric" },
	timeOptions: {
		hour: "numeric",
		minute: "2-digit",
		second: "2-digit",
		hour12: true,
	},
});

const statusVariant = computed(() => {
	if (props.entry.entryType !== "execution") return "neutral";
	const variants = {
		success: "success",
		error: "error",
		stopped: "warning",
	};
	return variants[props.entry.result] || "neutral";
});
</script>

<style scoped>
.header {
	padding: 20px;
	border-bottom: 1px solid var(--wdsColorGray2);
	background-color: var(--wdsColorGray1);
}

.header__title {
	display: flex;
	align-items: center;
	gap: 12px;
	margin-bottom: 12px;
}

.header__title h3 {
	margin: 0;
	font-size: 18px;
	font-weight: 600;
	color: var(--wdsColorBlack);
}

.header__meta {
	display: flex;
	gap: 16px;
	font-size: 14px;
	color: var(--wdsColorGray5);
}

.header__meta span:not(:last-child)::after {
	content: "•";
	margin-left: 16px;
	color: var(--wdsColorGray4);
}
</style>
