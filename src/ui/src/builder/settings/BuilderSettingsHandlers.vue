<template>
	<div
		v-if="shoudBeDisplayed"
		:inert="isReadOnly"
		class="BuilderSettingsHandlers"
	>
		<WdsTitle2 class="BuilderSettingsHandlers__title">Blueprints</WdsTitle2>
		<div class="BuilderSettingsHandlers__list">
			<div
				v-for="(eventInfo, eventType) in recognisedEvents"
				:key="eventType"
			>
				<BuilderSettingsHandlersBlueprint
					:component="component"
					:event-type="eventType"
					:event-description="eventInfo.desc"
				/>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ComputedRef, inject } from "vue";

import injectionKeys from "@/injectionKeys";
import { InstancePath, WriterComponentDefinition } from "@/writerTypes";
import BuilderSettingsHandlersBlueprint from "./BuilderSettingsHandlersBlueprint.vue";
import WdsTitle2 from "@/wds/WdsTitle2.vue";
import { useEvaluator } from "@/renderer/useEvaluator";
import { parseInstancePathString } from "@/renderer/instancePath";

defineProps({
	isReadOnly: { type: Boolean },
});

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const secretsManager = inject(injectionKeys.secretsManager);

const component = computed(() =>
	wf.getComponentById(wfbm.firstSelectedId.value),
);
const selectedInstancePath = computed<InstancePath>(() =>
	parseInstancePathString(wfbm.firstSelectedItem?.value?.instancePath),
);

const { getEvaluatedFields } = useEvaluator(wf, secretsManager);
const evaluatedFields = computed(() =>
	getEvaluatedFields(selectedInstancePath.value),
);

const recognisedEvents: ComputedRef<WriterComponentDefinition["events"]> =
	computed(() => {
		if (!component.value) return {};
		const { type } = component.value;
		const componentDefinition = wf.getComponentDefinition(type);
		const supportedEvents = componentDefinition?.events ?? {};

		const entries = Object.entries(supportedEvents).filter(([_, v]) => {
			if (v.enabled === undefined) return true;
			return v.enabled({ evaluatedFields: evaluatedFields.value });
		});
		const recEvents = Object.fromEntries(entries);

		Object.keys({ ...component.value.handlers }).forEach((eventType) => {
			if (recEvents[eventType]) return;
			recEvents[eventType] = { desc: "Custom event" };
		});

		return recEvents;
	});

const shoudBeDisplayed = computed(() => {
	if (!wfbm.isSingleSelectionActive.value) return false;
	return Object.keys(recognisedEvents.value).length > 0;
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsHandlers {
	padding: 24px;
}

.BuilderSettingsHandlers[inert] {
	opacity: 0.7;
}

.BuilderSettingsHandlers__title {
	padding-bottom: 16px;
}

.BuilderSettingsHandlers__list {
	display: flex;
	flex-direction: column;
	gap: 24px;
}
</style>
