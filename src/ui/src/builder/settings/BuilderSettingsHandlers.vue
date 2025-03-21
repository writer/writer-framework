<template>
	<div v-if="shoudBeDisplayed" class="BuilderSettingsHandlers">
		<div class="BuilderSettingsHandlers__title">
			<i class="material-symbols-outlined">linked_services</i>
			<h3>Blueprints</h3>
		</div>
		<div class="BuilderSettingsHandlers__list">
			<div
				v-for="(eventInfo, eventType) in recognisedEvents"
				:key="eventType"
			>
				<BuilderSettingsHandlersWorkflow
					:component="component"
					:event-type="eventType"
					:event-description="eventInfo.desc"
				/>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
// TODO: rename this component
import { computed, ComputedRef, inject } from "vue";
import injectionKeys from "@/injectionKeys";
import { WriterComponentDefinition } from "@/writerTypes";
import BuilderSettingsHandlersWorkflow from "./BuilderSettingsHandlersWorkflow.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(wfbm.firstSelectedId.value),
);

const recognisedEvents: ComputedRef<WriterComponentDefinition["events"]> =
	computed(() => {
		const { type } = component.value;
		const { events: supportedEvents } = wf.getComponentDefinition(type);

		const recEvents = { ...supportedEvents };

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

.BuilderSettingsHandlers__title {
	padding-bottom: 24px;
	display: flex;
	gap: 8px;
	align-items: center;
	font-size: 1rem;
}

.BuilderSettingsHandlers__list {
	display: flex;
	flex-direction: column;
	gap: 24px;
}
</style>
