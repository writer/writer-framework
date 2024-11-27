<template>
	<div class="BuilderLogIndicator">
		<div v-if="entryCountByType['error'] > 0" class="number error">
			<div class="icon">
				<i class="material-symbols-outlined">error</i>
			</div>
			{{ entryCountByType["error"] ?? 0 }}
		</div>
		<div v-if="entryCountByType['info'] > 0" class="number info">
			<div class="icon">
				<i class="material-symbols-outlined">info</i>
			</div>
			{{ entryCountByType["info"] ?? 0 }}
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";

const wfbm = inject(injectionKeys.builderManager);

const entryCountByType = computed(() => {
	return wfbm.getLogEntries().reduce((accumulator, currentValue) => {
		if (!(currentValue.type in accumulator)) {
			accumulator[currentValue.type] = 0;
		}
		accumulator[currentValue.type]++;
		return accumulator;
	}, {});
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderLogIndicator {
	font-size: 14px;
	font-weight: 400;
	display: flex;
	flex-wrap: wrap;
	justify-content: center;
	align-items: center;
	gap: 4px;
}

.number {
	border-radius: 30px;
	padding-right: 12px;
	border: 1px solid var(--builderSeparatorColor);
	display: flex;
	align-items: center;
	gap: 4px;
}

.icon {
	margin: 3px;
	border-radius: 50%;
	color: white;
	width: 16px;
	height: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.number.error .icon {
	background: #ff643c;
}

.number.info .icon {
	background: #6985ff;
}
</style>
