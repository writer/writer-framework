<template>
	<BuilderPanel
		panel-id="log"
		name="Log"
		:contents-teleport-el="contentsTeleportEl"
		:actions="actions"
		:scrollable="true"
		keyboard-shortcut-key="K"
		class="BuilderLogPanel"
		@openned="onOpenPanel"
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
				<BuilderLogBlueprintExecution
					v-if="logEntry.blueprintExecution"
					:execution-log="logEntry.blueprintExecution"
				>
				</BuilderLogBlueprintExecution>
			</template>
		</div>
		<div v-if="logEntries.length == 0" class="emptyMessage">
			<div>
				Exceptions and other relevant messages will be shown here.<br />Also,
				you can include print statements in event handlers to create log
				entries.
			</div>
		</div>
	</BuilderPanel>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import BuilderPanel, { type BuilderPanelAction } from "./BuilderPanel.vue";
import BuilderLogBlueprintExecution from "./BuilderLogBlueprintExecution.vue";
import injectionKeys from "@/injectionKeys";
import BuilderLogIndicator from "./BuilderLogIndicator.vue";
import { useWriterTracking } from "@/composables/useWriterTracking";

defineProps<{
	contentsTeleportEl: HTMLElement;
}>();

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const tracking = useWriterTracking(wf);

function onOpenPanel(open: boolean) {
	if (open) tracking.track("nav_logs_opened");
}

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
.entries {
	padding: 20px;
	display: flex;
	flex-direction: column;
	font-size: 14px;
	font-weight: 400;
	line-height: 140%;
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
	margin-top: 12px;
}

.entry.error {
	border: 1px solid var(--wdsColorOrange2);
	background: var(--wdsColorOrange1);
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
	white-space: pre-line;
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
