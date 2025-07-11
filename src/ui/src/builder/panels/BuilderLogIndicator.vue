<template>
	<div class="BuilderLogIndicator">
		<div v-if="entryCountByType['error'] > 0" class="number error">
			<div class="icon">
				<WdsIcon name="triangle-alert" />
			</div>
			{{ entryCountByType["error"] ?? 0 }}
		</div>
		<div v-if="entryCountByType['info'] > 0" class="number info">
			<div class="icon">
				<WdsIcon name="info" />
			</div>
			{{ entryCountByType["info"] ?? 0 }}
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsIcon from "@/wds/WdsIcon.vue";

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
	font-size: 12px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.number.error .icon {
	background: var(--wdsColorOrange5);
}

.number.info .icon {
	background: var(--wdsColorBlue4);
}
</style>
