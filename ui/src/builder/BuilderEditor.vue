<template>
	<div
		class="BuilderEditor"
		ref="builderEditor"
		:class="{
			dark: theme == 'vs-dark',
			light: theme == 'vs-light',
			activeLog: isLogActive,
		}"
	>
		<div class="editor">
			<div class="windowBar">
				<div class="icon"><i class="ri-code-line ri-lg"></i></div>
				<div class="title">Code Editor</div>
				<button
					class="windowAction"
					tabindex="0"
					:title="(theme == 'vs-light' ? 'Dark' : 'Light') + ' theme'"
					v-on:click="toggleTheme"
				>
					<i
						class="ri-sun-line ri-lg"
						v-show="theme == 'vs-dark'"
					></i>
					<i
						class="ri-moon-line ri-lg"
						v-show="theme == 'vs-light'"
					></i>
				</button>
			</div>
			<div class="codeActions">
				<button v-on:click="save" :disabled="editorDisabled">
					<i class="ri-save-line"></i>{{ "Save and run" }}
					<div
						class="saveTick"
						:class="{ saved: isCodeSaved }"
						title="Code is saved"
					>
						<i class="ri-check-line"></i>
					</div>
				</button>
				<button
					v-on:click="run"
					:disabled="editorDisabled"
					v-if="false"
				>
					<i class="ri-play-line"></i>Run
				</button>
				<div class="statusMessage" v-if="statusMessage">
					<div class="statusOk ok" v-if="statusMessage.ok === true">
						<i class="ri-check-line"></i>
					</div>
					<div
						class="statusOk notOk"
						v-else-if="statusMessage.ok === false"
					>
						<i class="ri-error-warning-line"></i>
					</div>
					<div
						class="statusOk processing"
						v-else-if="statusMessage.ok === 'processing'"
					>
						<i class="ri-loader-3-line"></i>
					</div>
					{{ statusMessage.message }}
				</div>
			</div>
			<div ref="editorContainer" class="editorContainer"></div>
		</div>
		<div class="log">
			<div class="windowBar">
				<div class="icon"><i class="ri-booklet-line"></i></div>
				<div class="title">
					Log <span class="countLabel">{{ logEntries.length }}</span>
				</div>
				<button
					class="windowAction"
					tabindex="0"
					title="Clear log"
					v-on:click="ssbm.clearLogEntries"
				>
					<i class="ri-delete-bin-line"></i>
				</button>
				<button
					class="windowAction"
					tabindex="0"
					v-on:click="toggleLog"
					:title="(isLogActive ? 'Hide' : 'Show') + ' log'"
				>
					<i
						class="ri-arrow-drop-up-line ri-lg"
						v-show="!isLogActive"
					></i>
					<i
						class="ri-arrow-drop-down-line ri-lg"
						v-show="isLogActive"
					></i>
				</button>
			</div>
			<div class="entryContainer" v-if="isLogActive">
				<div class="entry" v-for="logEntry in logEntries">
					<div class="icon" :class="logEntry.type">
						<i
							:class="logEntryTypeIcon[logEntry.type]"
							class="ri-xl"
						></i>
					</div>
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
							<div class="codeContainer" v-if="logEntry.code">
								<code>{{ logEntry.code }}</code>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";

import {
	inject,
	onMounted,
	onUnmounted,
	Ref,
	ref,
	watch,
	nextTick,
	computed,
} from "vue";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const builderEditor: Ref<HTMLElement> = ref(null);
const editorContainer: Ref<HTMLElement> = ref(null);
const editorDisabled: Ref<boolean> = ref(false);
let editor: monaco.editor.IStandaloneCodeEditor = null;

const theme: Ref<string> = ref("vs-light");
const isLogActive: Ref<boolean> = ref(ssbm.getLogEntryCount() > 0);
const isCodeSaved: Ref<boolean> = ref(ss.getSavedCode() === ss.getRunCode());

type StatusMessage = {
	ok: boolean | "processing";
	message: string;
};

const statusMessage: Ref<StatusMessage> = ref(null);

const logEntryTypeIcon: Record<string, string> = {
	error: "ri-error-warning-fill",
	info: "ri-information-fill",
};

const logEntries = computed(() => {
	return ssbm.getLogEntries();
});

const handleLogEntry = () => {
	isLogActive.value = true;
};

onMounted(() => {
	// Subscribe to new log entries to open log section, but ignore content of log entry.

	ss.addMailSubscription("logEntry", handleLogEntry);
	const targetEl = editorContainer.value;
	editor = monaco.editor.create(targetEl, {
		value: ss.getRunCode(),
		language: "python",
		theme: theme.value,
	});
	editor.getModel().onDidChangeContent(() => {
		isCodeSaved.value = false;
		statusMessage.value = null;
	});
	window.addEventListener("resize", updateDimensions.bind(this));
});

onUnmounted(() => {
	window.removeEventListener("resize", updateDimensions.bind(this));
});

watch(
	() => ss.getRunCode(),
	(newRunCode) => {
		editor.getModel().setValue(newRunCode);
		isCodeSaved.value = ss.getSavedCode() === ss.getRunCode();
	}
);

watch(
	() => ssbm.getMode(),
	(newMode) => {
		if (newMode !== "code") return;
		nextTick(() => {
			editor.layout();
		});
	}
);

const disableEditor = () => {
	editorDisabled.value = true;
	editor.updateOptions({ readOnly: true });
};

const enableEditor = () => {
	editorDisabled.value = false;
	editor.updateOptions({ readOnly: false });
};

const save = async () => {
	const editorCode = editor.getValue();
	statusMessage.value = {
		ok: "processing",
		message: `Processing...`,
	};
	try {
		disableEditor();
		await ss.sendCodeSaveRequest(editorCode);
	} catch (error) {
		statusMessage.value = {
			ok: false,
			message: `Code hasn't been saved. ${error}`,
		};
		return;
	} finally {
		enableEditor();
	}
	statusMessage.value = null;
	isCodeSaved.value = true;
};

const run = async () => {
	const editorCode = editor.getValue();
	statusMessage.value = {
		ok: "processing",
		message: `Processing...`,
	};
	try {
		disableEditor();
		await ss.sendCodeUpdate(editorCode);
	} catch (error) {
		statusMessage.value = {
			ok: false,
			message: `Code hasn't run. ${error}`,
		};
		return;
	} finally {
		enableEditor();
	}
	statusMessage.value = { ok: true, message: "Code has been executed." };
};

const toggleLog = () => {
	isLogActive.value = !isLogActive.value;

	nextTick(() => {
		editor.layout();
	});
};

const toggleTheme = () => {
	if (theme.value == "vs-light") {
		theme.value = "vs-dark";
	} else {
		theme.value = "vs-light";
	}

	editor.updateOptions({
		theme: theme.value,
	});
};

const updateDimensions = () => {
	editor.layout();
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderEditor {
	width: 100%;
	height: 100%;
	display: grid;
	grid-template-columns: 1fr;
	grid-template-rows: 76fr 47fr;
	color: var(--builderPrimaryTextColor);
}

.BuilderEditor:not(.activeLog) {
	grid-template-rows: 76fr 48px;
}

.BuilderEditor.light {
	background: white;
}

.BuilderEditor.dark {
	background: #1e1e1e;
	--builderPrimaryTextColor: #f0f0f0;
	--builderSecondaryTextColor: #c0c0c0;
	--builderSubtleHighlightColorSolid: #2b2b2b;
	--builderSubtleSeparatorColor: rgba(255, 255, 255, 0.05);
}

.dark button {
	background: #1e1e1e;
	border: 1px solid var(--builderSubtleSeparatorColor);
	color: var(--builderPrimaryTextColor);
}

.editor {
	grid-column: 1;
	grid-row: 1;
	overflow: hidden;
	display: flex;
	flex-direction: column;
}

.editor .windowBar {
	flex: 0 0 auto;
}

.editor .codeActions {
	padding: 16px;
	display: flex;
	gap: 16px;
	flex: 0 0 auto;
	align-items: center;
}

.editor .codeActions button[disabled] {
	color: var(--builderDisabledColor);
}

.editor .saveTick {
	display: none;
	width: 16px;
	height: 16px;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
	background: var(--builderDisabledColor);
	color: var(--builderBackgroundColor);
	transition: 0.2s all ease-in-out;
}

.editor .saveTick.saved {
	display: flex;
	background: var(--builderSecondaryTextColor);
}

.editor .statusMessage {
	display: flex;
	align-items: center;
	overflow: hidden;
}

.editor .statusMessage .statusOk {
	margin-right: 8px;
	display: flex;
	align-items: center;
}

.editor .statusMessage .statusOk.ok {
	color: var(--builderSuccessColor);
}

.editor .statusMessage .statusOk.notOk {
	color: var(--builderErrorColor);
}

.editor .editorContainer {
	flex: 1 0 0;
	overflow: hidden;
}

.log {
	overflow-y: auto;
	overflow-x: hidden;
	grid-column: 1;
	grid-row: 2;
	display: flex;
	flex-direction: column;
}

.entryContainer {
	flex: 1 0 auto;
}

.entryContainer:empty {
	display: flex;
	align-items: center;
	text-align: center;
	justify-content: center;
	padding: 16px;
}

.entryContainer:empty::after {
	content: "Exceptions and other relevant messages will be shown here. Also, you can include print statements in event handlers to create log entries.";
}

.entry {
	display: flex;
	align-items: center;
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	width: 100%;
}

.entry .icon {
	flex: 0 0 72px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.entry .icon.error {
	color: #ff5d00;
}

.entry .icon.info {
	color: #0094d1;
}

.entry .content {
	flex: 1 1 auto;
	padding: 16px 16px 16px 0;
}

.entry .content .message {
	white-space: pre-wrap;
}

.entry .header {
	display: flex;
	margin-bottom: 4px;
}

.entry .header .title {
	flex: 1 0 auto;
	color: var(--builderSecondaryTextColor);
}

.entry .header .time {
	color: var(--builderSecondaryTextColor);
}

/* This pre tag tells the Prettier formatter to respect whitespace. */
.entry .content {
	font-family: inherit;
	margin: 0;
	white-space: pre-wrap;
}

.entry .content code {
	margin: 0;
	white-space: pre-wrap;
}

.entry .codeContainer {
	max-width: 100%;
	margin-top: 16px;
}
.entry code {
	margin: 0;
	width: 100%;
	max-height: 100%;
}
</style>
