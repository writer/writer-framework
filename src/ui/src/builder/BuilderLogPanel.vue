<template>
	<BuilderPanel
		panel-id="log"
		name="Log"
		:actions="actions"
		tabindex="0"
		class="BuilderLogPanel"
	>
		<template #titleCompanion>
			<BuilderLogIndicator></BuilderLogIndicator>
		</template>
		<div v-if="logEntries.length > 0" class="entries">
			<template v-for="(logEntry, index) in logEntries" :key="index">
				<div class="entry" :class="logEntry.type">
					<div class="icon">
						<i
							v-if="logEntry.type == 'error'"
							class="material-symbols-outlined"
							>error</i
						>
						<i v-else class="material-symbols-outlined">info</i>
					</div>
					<div class="title">
						{{ logEntry.title
						}}{{
							logEntry.repeated > 0
								? ` · Repeated ${logEntry.repeated} times`
								: ""
						}}
					</div>
					<div class="time">
						{{ logEntry.timestampReceived.toLocaleTimeString() }}
					</div>
					<div class="content">
						{{ logEntry.message }}
						<div v-if="logEntry.code" class="codeContainer">
							<code>{{ logEntry.code }}</code>
						</div>
					</div>
				</div>
				<BuilderLogWorkflowExecution
					v-if="logEntry.workflowExecution"
					:execution-log="logEntry.workflowExecution"
				>
				</BuilderLogWorkflowExecution>
			</template>
		</div>
		<div v-if="logEntries.length == 0" class="emptyMessage">
			<div>
				Exceptions and other relevant messages will be shown here.<br />Also,
				you can include print statements in event handlers to create log
				entries.
			</div>
		</div>
		<!-- <div v-for="(logEntry, index) in logEntries" :key="index" class="entry">
			<div class="icon" :class="logEntry.type"></div>
			<div class="content">
				<div class="header">
					<span class="title"
						></span
					>
					<span class="time"></span>
				</div>
				<div class="message">
					{{ logEntry.message }}
					<div v-if="logEntry.code" class="codeContainer">
						<code>{{ logEntry.code }}</code>
					</div>
				</div>
			</div>
		</div> -->
	</BuilderPanel>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import BuilderPanel, { type BuilderPanelAction } from "./BuilderPanel.vue";
import BuilderLogWorkflowExecution from "./BuilderLogWorkflowExecution.vue";
import injectionKeys from "@/injectionKeys";
import BuilderLogIndicator from "./BuilderLogIndicator.vue";

const wfbm = inject(injectionKeys.builderManager);

const actions: BuilderPanelAction[] = [
	{
		icon: "delete",
		name: "Clear log",
		callback: () => {
			wfbm.clearLogEntries();
		},
		keyboardShortcut: {
			modifierKey: true,
			key: "L",
		},
	},
];

const logEntries = computed(() => {
	return wfbm.getLogEntries();
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderLogPanel {
	font-size: 14px;
	font-weight: 400;
	line-height: 140%;
}

.entries {
	padding: 20px;
	display: flex;
	flex-direction: column;
}

.entry {
	padding: 8px 8px 8px 0;
	border-radius: 6px;
	border: 1px solid var(--builderSeparatorColor);
	display: grid;
	grid-template-columns: 40px 1fr 80px;
	grid-template-rows: auto 1fr;
}

.entry:not(:first-of-type) {
	margin-top: 10px;
}

.entry.error {
	border: 1px solid #ffcfc2;
	background: #fff4f1;
}

.entry .icon {
	font-size: 20px;
	display: flex;
	align-items: center;
	justify-content: center;
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	color: var(--builderAccentColor);
}

.entry.error .icon {
	color: var(--builderErrorColor);
}

.entry .title {
	font-weight: 500;
}

.entry .time {
	grid-column: 3 / 4;
	grid-row: 1 / 2;
}

.entry .content {
	margin-top: 4px;
	grid-column: 2 / 4;
	grid-row: 2 / 3;
	overflow: hidden;
}

.entry .content .codeContainer {
	max-width: 100%;
	margin-top: 10px;
	padding: 8px;
	border-radius: 6px;
	overflow: auto;
	background-color: rgba(0, 0, 0, 0.03);
}

.entry .content code {
	margin: 0;
	font-size: 12px;
	white-space: pre-wrap;
	margin: 0;
	width: 100%;
	max-height: 100%;
}

.emptyMessage {
	padding: 20px;
	display: flex;
	width: 100%;
	height: 100%;
	justify-content: center;
	align-items: center;
	text-align: center;
}
</style>
