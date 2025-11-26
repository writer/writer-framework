<template>
	<div class="metadata">
		<!-- Execution Metadata -->
		<template v-if="entry.entryType === 'execution'">
			<div class="metadata__section">
				<h4>Trigger Information</h4>
				<div class="metadata__row">
					<span class="label">Type:</span>
					<span>{{ entry.trigger.type }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Event:</span>
					<span>{{ entry.trigger.event }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Component ID:</span>
					<span>{{ entry.trigger.component.id }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Component Type:</span>
					<span>{{ entry.trigger.component.type }}</span>
				</div>
			</div>

			<div class="metadata__section">
				<h4>Execution Information</h4>
				<div class="metadata__row">
					<span class="label">Timestamp:</span>
					<span>{{ entry.timestamp }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Instance Type:</span>
					<span>{{ entry.instanceTypeLabel }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Result:</span>
					<span>{{ entry.result }}</span>
				</div>
			</div>
		</template>

		<!-- Init Log Metadata -->
		<template v-else>
			<div class="metadata__section">
				<h4>Initialization Information</h4>
				<div class="metadata__row">
					<span class="label">Timestamp:</span>
					<span>{{ entry.timestamp }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Instance Type:</span>
					<span>{{ entry.instanceTypeLabel }}</span>
				</div>
				<div class="metadata__row">
					<span class="label">Mode:</span>
					<span>{{ entry.mode }}</span>
				</div>
			</div>
		</template>
	</div>
</template>

<script setup lang="ts">
import { PropType } from "vue";
import { UnifiedEntry } from "../BuilderJournal.vue";

defineProps({
	entry: { type: Object as PropType<UnifiedEntry>, required: true },
});
</script>

<style scoped>
.metadata {
	padding: 20px;
}

.metadata__section {
	margin-bottom: 24px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.metadata__section h4 {
	margin: 0 0 12px 0;
	font-size: 14px;
	font-weight: 600;
	color: var(--wdsColorBlack);
}

.metadata__row {
	display: flex;
	gap: 12px;
	font-size: 14px;
	padding-bottom: 4px;
	border-bottom: 0.5px solid var(--wdsColorGray2);
}

.metadata__row .label {
	font-weight: 500;
	color: var(--wdsColorGray6);
	min-width: 140px;
}

.metadata__row span:not(.label) {
	color: var(--wdsColorGray7);
	word-break: break-all;
}
</style>
