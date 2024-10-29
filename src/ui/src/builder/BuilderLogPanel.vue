<template>
	<BuilderPanel name="Log" :actions="actions" class="BuilderLogPanel">
		<div v-for="(logEntry, index) in logEntries" :key="index" class="entry">
			<div class="icon" :class="logEntry.type"></div>
			<div class="content">
				<div class="header">
					<span class="title"
						>{{ logEntry.title
						}}{{
							logEntry.repeated > 0
								? ` · Repeated ${logEntry.repeated} times`
								: ""
						}}</span
					>
					<span class="time">{{
						logEntry.timestampReceived.toLocaleTimeString()
					}}</span>
				</div>
				<div class="message">
					{{ logEntry.message }}
					<div v-if="logEntry.code" class="codeContainer">
						<code>{{ logEntry.code }}</code>
					</div>
					<BuilderLogWorkflowExecution
						v-if="logEntry.workflowExecution"
						:execution-log="logEntry.workflowExecution"
					>
					</BuilderLogWorkflowExecution>
				</div>
			</div>
		</div>
	</BuilderPanel>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import BuilderPanel, { type BuilderPanelAction } from "./BuilderPanel.vue";
import injectionKeys from "@/injectionKeys";

const wf = inject(injectionKeys.core);

const wfbm = inject(injectionKeys.builderManager);

const actions: BuilderPanelAction[] = [
	{
		icon: "close",
		callback: () => {
			wfbm.openPanels.delete("log");
		},
	},
];

const logEntries = computed(() => {
	return wfbm.getLogEntries();
});
</script>

<style scoped>
@import "./sharedStyles.css";
</style>
