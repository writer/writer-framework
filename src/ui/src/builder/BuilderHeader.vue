<template>
	<div class="BuilderHeader">
		<div v-if="canDeploy" class="BuilderHeader__appTitle">
			<a
				:href="writerDeployUrl.toString()"
				class="BuilderHeader__appTitle__goBack"
			>
				<i class="material-symbols-outlined">arrow_back</i>
			</a>
			<input
				v-model="applicationName"
				type="text"
				class="BuilderHeader__appTitle__input"
			/>
		</div>
		<img v-else src="../assets/logo.svg" alt="Writer Framework logo" />
		<BuilderSwitcher />
		<div class="gap"></div>
		<div class="BuilderHeader__toolbar">
			<button
				type="button"
				class="BuilderHeader__toolbar__btn"
				data-automation-key="undo"
				:data-writer-tooltip="
					undoRedoSnapshot.isUndoAvailable
						? `Undo: ${undoRedoSnapshot.undoDesc}`
						: 'Nothing to undo'
				"
				:disabled="!undoRedoSnapshot.isUndoAvailable"
				data-writer-tooltip-placement="bottom"
				@click="undo()"
			>
				<i class="material-symbols-outlined">undo</i>
			</button>
			<button
				type="button"
				class="BuilderHeader__toolbar__btn"
				data-automation-key="redo"
				:data-writer-tooltip="
					undoRedoSnapshot.isRedoAvailable
						? `Redo: ${undoRedoSnapshot.redoDesc}`
						: 'Nothing to redo'
				"
				:disabled="!undoRedoSnapshot.isRedoAvailable"
				data-writer-tooltip-placement="bottom"
				@click="redo()"
			>
				<i class="material-symbols-outlined">redo</i>
			</button>
			<button
				type="button"
				class="BuilderHeader__toolbar__btn"
				data-writer-tooltip="State Explorer"
				data-writer-tooltip-placement="bottom"
				@click="showStateExplorer"
			>
				<i class="material-symbols-outlined">mystery</i>
			</button>
			<WdsButton
				v-if="canDeploy"
				size="small"
				:loading="isDeploying"
				:data-writer-tooltip="deployTooltip"
				data-writer-tooltip-placement="bottom"
				data-automation-key="deploy"
				@click="requestDeployment"
			>
				{{ deployLabel }}
				<WdsModal
					v-if="confirmDeployModalOpen"
					title="Are you sure you want to deploy these changes?"
					size="normal"
					:actions="confirmDeployModalActions"
					data-automation-key="deployConfirmModal"
				>
					<p>
						This will replace the current live version of this agent
						everywhere it is currently deployed.
					</p>
				</WdsModal>
			</WdsButton>
			<WdsStateDot
				:state="stateDotState"
				:data-writer-tooltip="syncHealthStatus"
				data-writer-tooltip-placement="left"
			/>
			<WdsModal
				v-if="isStateExplorerShown"
				title="State Explorer"
				display-close-button
				@close="isStateExplorerShown = false"
			>
				<BuilderStateExplorer />
			</WdsModal>
		</div>
	</div>
</template>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import BuilderSwitcher from "./BuilderSwitcher.vue";
import { useComponentActions } from "./useComponentActions";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import injectionKeys from "@/injectionKeys";
import BuilderStateExplorer from "./BuilderStateExplorer.vue";
import WdsStateDot, { WdsStateDotState } from "@/wds/WdsStateDot.vue";
import { useApplicationCloud } from "@/composables/useApplicationCloud";
import WdsButton from "@/wds/WdsButton.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { undo, redo, getUndoRedoSnapshot } = useComponentActions(wf, ssbm);
const isStateExplorerShown: Ref<boolean> = ref(false);

const {
	canDeploy,
	isDeploying,
	publishApplication,
	hasBeenPublished,
	lastDeployedAt,
	name: applicationName,
	writerDeployUrl,
} = useApplicationCloud(wf);

const undoRedoSnapshot = computed(() => getUndoRedoSnapshot());

const dateFormater = new Intl.DateTimeFormat(undefined, {
	weekday: "long",
	year: "numeric",
	month: "long",
	day: "numeric",
	hour: "numeric",
	minute: "numeric",
});

async function requestDeployment() {
	if (hasBeenPublished.value) {
		confirmDeployModalOpen.value = true;
	} else {
		await publishApplication();
	}
}

const confirmDeployModalOpen = ref(false);
const confirmDeployModalActions: ModalAction[] = [
	{ desc: "Cancel", fn: () => (confirmDeployModalOpen.value = false) },
	{
		desc: "Yes, deploy changes",
		fn: async () => {
			confirmDeployModalOpen.value = false;
			await publishApplication();
		},
	},
];

const deployTooltip = computed(() => {
	if (!lastDeployedAt.value) return;
	const date = dateFormater.format(lastDeployedAt.value);
	return `Editor Last saved ${date}`;
});
const deployLabel = computed(() => {
	if (hasBeenPublished.value === true) return "Deploy changes";
	if (hasBeenPublished.value === false) return "Configure deployment";
	return "Configure deployment";
});

const syncHealthStatus = computed(() => {
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
});

const stateDotState = computed<WdsStateDotState>(() => {
	switch (wf.syncHealth.value) {
		case "offline":
		case "suspended":
		case "idle":
			return "error";
		default:
			return "deployed";
	}
});

function showStateExplorer() {
	isStateExplorerShown.value = true;
}
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

.BuilderHeader__appTitle {
	height: 100%;
	display: flex;
	gap: 8px;
	align-items: center;
	width: calc(var(--builderSidebarWidth) - 16px);
	padding-right: 16px;
	border-right: 1px solid var(--wdsColorGray5);
}
.BuilderHeader__appTitle__goBack {
	text-decoration: none;
}
.BuilderHeader__appTitle__input {
	background-color: transparent;
	width: 100%;
	border: none;
	font-weight: 500;
	font-size: 18px;
	border-radius: 4px;
	padding: 4px;
	height: 32px;
}
.BuilderHeader__appTitle__input:hover,
.BuilderHeader__appTitle__input:focus {
	outline: none;
	background-color: var(--wdsColorGray5);
}

.BuilderHeader__toolbar {
	display: flex;
	align-items: center;
	gap: 8px;
}

.BuilderHeader__toolbar__btn {
	background: var(--builderHeaderBackgroundHoleColor);
	color: var(--builderBackgroundColor);
	border: none;
	border-radius: 50%;
	height: 32px;
	width: 32px;

	display: flex;
	align-items: center;
	justify-content: center;

	font-size: 14px;
}

.BuilderHeader img {
	width: 28px;
}

.BuilderHeader .gap {
	flex: 1 0 auto;
}

.panelToggler,
.panelToggler:hover {
	font-size: 12px;
	--buttonColor: black;
	--builderSeparatorColor: var(--wdsColorGray6);
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

button {
	background: unset;
	color: var(--builderBackgroundColor);
}
</style>
