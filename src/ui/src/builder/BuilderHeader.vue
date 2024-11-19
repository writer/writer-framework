<template>
	<div class="BuilderHeader">
		<img src="../assets/logo.svg" alt="Writer Framework logo" />
		<BuilderSwitcher></BuilderSwitcher>
		<div class="undoRedo">
			<button
				class="undo"
				:title="
					undoRedoSnapshot.isUndoAvailable
						? `Undo ${undoRedoSnapshot.undoDesc}`
						: 'Nothing to undo'
				"
				:disabled="!undoRedoSnapshot.isUndoAvailable"
				@click="undo()"
			>
				<i class="material-symbols-outlined"> undo </i>
				Undo
			</button>
			<button
				class="redo"
				:title="
					undoRedoSnapshot.isRedoAvailable
						? `Redo ${undoRedoSnapshot.redoDesc}`
						: 'Nothing to redo'
				"
				:disabled="!undoRedoSnapshot.isRedoAvailable"
				@click="redo()"
			>
				<i class="material-symbols-outlined"> redo </i>
				Redo
			</button>
		</div>
		<div>
			<button @click="showStateExplorer">
				<i class="material-symbols-outlined"> mystery </i>
				State Explorer
			</button>
			<BuilderModal
				v-if="isStateExplorerShown"
				:close-action="customHandlerModalCloseAction"
				icon="mystery"
				modal-title="State Explorer"
			>
				<BuilderStateExplorer></BuilderStateExplorer>
			</BuilderModal>
		</div>
		<div class="gap"></div>
		<WdsButton
			variant="primary"
			size="small"
			class="panelToggler"
			data-automation-action="toggle-code-panel"
			:class="{ active: ssbm.openPanels.has('code') }"
			@click="togglePanel('code')"
		>
			<i class="material-symbols-outlined"> code </i>
			Code
		</WdsButton>
		<WdsButton
			variant="primary"
			size="small"
			class="panelToggler"
			data-automation-action="toggle-log-panel"
			title="Toggle Log panel"
			:class="{ active: ssbm.openPanels.has('log') }"
			@click="togglePanel('log')"
		>
			Log
			<BuilderLogIndicator class="indicator"></BuilderLogIndicator>
		</WdsButton>
		<div
			class="syncHealth"
			:class="wf.syncHealth.value"
			:title="syncHealthStatus()"
		>
			<i ref="syncHealthIcon" class="material-symbols-outlined icon"
				>sync</i
			><span v-if="wf.syncHealth.value == 'offline'">Offline</span>
		</div>
	</div>
</template>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import BuilderSwitcher from "./BuilderSwitcher.vue";
import { useComponentActions } from "./useComponentActions";
import BuilderModal, { ModalAction } from "./BuilderModal.vue";
import injectionKeys from "../injectionKeys";
import BuilderStateExplorer from "./BuilderStateExplorer.vue";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderLogIndicator from "./BuilderLogIndicator.vue";

const syncHealthIcon = ref(null);
const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { undo, redo, getUndoRedoSnapshot } = useComponentActions(wf, ssbm);
const isStateExplorerShown: Ref<boolean> = ref(false);

const undoRedoSnapshot = computed(() => getUndoRedoSnapshot());

const syncHealthStatus = () => {
	let s = "";
	switch (wf.syncHealth.value) {
		case "offline":
			s += "Offline. Not syncing.";
			break;
		case "connected":
			s += "Online. Syncing...";
			break;
		case "idle":
			s += "Sync not initialised.";
			break;
		case "suspended":
			s += "Sync suspended.";
			break;
	}

	if (wf.featureFlags.value.length > 0) {
		s += ` Feature flags: ${wf.featureFlags.value.join(", ")}`;
	}

	return s;
};

function showStateExplorer() {
	isStateExplorerShown.value = true;
}

function togglePanel(
	panelId: typeof ssbm.openPanels extends Set<infer T> ? T : never,
) {
	if (ssbm.openPanels.has(panelId)) {
		ssbm.openPanels.delete(panelId);
		return;
	}
	ssbm.openPanels.add(panelId);
}

const customHandlerModalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		isStateExplorerShown.value = false;
	},
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderHeader {
	background: var(--builderHeaderBackgroundColor);
	color: var(--builderBackgroundColor);
	padding: 0 12px 0 16px;
	display: flex;
	align-items: center;
	gap: 16px;
	padding-top: 1px;
	border-bottom: 1px solid var(--builderAreaSeparatorColor);
}

.BuilderHeader img {
	width: 28px;
}

.undoRedo {
	display: flex;
	align-items: center;
	gap: 8px;
}
.BuilderHeader .gap {
	flex: 1 0 auto;
}

.panelToggler,
.panelToggler:hover {
	font-size: 12px;
	--buttonColor: black;
	--builderSeparatorColor: #303030;
	--buttonTextColor: white;
}

.panelToggler:focus {
	outline: 1px solid #606060;
	background: var(--buttonColor);
}

.panelToggler.active,
.panelToggler.active:focus {
	--buttonColor: white;
	--buttonTextColor: black;
	--builderSeparatorColor: unset;
	background: var(--buttonColor);
	color: var(--buttonTextColor);
}

.panelToggler .indicator {
	margin-right: -12px;
}

.syncHealth {
	background: var(--builderHeaderBackgroundHoleColor);
	border-radius: 18px;
	padding-left: 16px;
	padding-right: 16px;
	height: 32px;
	display: flex;
	gap: 8px;
	align-items: center;
	transition:
		color,
		background-color 0.5s ease-in-out;
}

.syncHealth.offline {
	background: var(--builderErrorColor);
}

.syncHealth.suspended {
	background: var(--builderErrorColor);
}

.syncHealth.connected {
	color: var(--builderBackgroundColor);
}

.syncHealth .icon {
	transform-origin: center;
	font-size: 0.875rem;
}

.syncHealth .icon.beingAnimated {
	animation-name: activate;
	animation-duration: 1s;
	animation-timing-function: ease-in-out;
}

@keyframes activate {
	0% {
		transform: rotate(0deg);
	}
	100% {
		transform: rotate(360deg);
	}
}

button {
	background: unset;
	color: var(--builderBackgroundColor);
}
</style>
