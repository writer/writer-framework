<template>
	<div class="BuilderHeader">
		<div class="BuilderHeader__logo">
			<a
				v-if="writerDeployUrl"
				:href="writerDeployUrl.toString()"
				target="_blank"
				class="BuilderHeader__goBack"
			>
				<img src="../assets/logo.svg" alt="Writer Framework logo" />
			</a>
			<img v-else src="../assets/logo.svg" alt="Writer Framework logo" />
			<hr />
			<input
				v-if="wf.isWriterCloudApp.value"
				v-model="applicationName"
				type="text"
				:disabled="!!lastDeployedAt"
				class="BuilderHeader__logo__appTitle"
			/>
		</div>
		<BuilderSwitcher class="BuilderHeader__switcher" />
		<div class="BuilderHeader__toolbar">
			<hr />
			<WdsButton
				variant="secondary"
				size="smallIcon"
				data-writer-tooltip="State Explorer"
				data-writer-tooltip-placement="bottom"
				@click="showStateExplorer"
			>
				<WdsIcon name="compass" />
			</WdsButton>
			<WdsButton
				variant="secondary"
				size="smallIcon"
				data-writer-tooltip="Invite collaborators"
				data-writer-tooltip-placement="bottom"
				@click="showInviteCollaborators"
			>
				<WdsIcon name="share-2" />
			</WdsButton>
			<BuilderHeaderMoreDropdown />
			<WdsButton
				v-if="canDeploy"
				size="small"
				class="BuilderHeader__toolbar__deployBtn"
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
				>
					<p class="BuilderHeader__toolbar__deployModal__text">
						This will replace the current live version of this agent
						everywhere it is currently deployed.
					</p>
				</WdsModal>
			</WdsButton>
			<BuilderHeaderConnected></BuilderHeaderConnected>
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
			<WdsModal
				v-if="isInviteCollaboratorsShown"
				title="Share edit link with collaborators"
				description="All AI Studio builders in your org can edit this agent with you in real time. Copy the link below to point them directly to editing this agent."
				display-close-button
				:actions="[
					{
						desc: 'Close',
						fn: () => (isInviteCollaboratorsShown = false),
					},
					{
						desc: clipboard.copied.value
							? 'Copied'
							: 'Copy edit link',
						fn: copyInviteCollaboratorsURL,
						icon: clipboard.copied.value ? 'check' : 'clipboard',
						disabled: clipboard.copied.value,
					},
				]"
				@close="isInviteCollaboratorsShown = false"
			>
			</WdsModal>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import BuilderSwitcher from "./BuilderSwitcher.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import injectionKeys from "@/injectionKeys";
import BuilderStateExplorer from "./BuilderStateExplorer.vue";
import WdsStateDot from "@/wds/WdsStateDot.vue";
import { useWriterAppDeployment } from "./useWriterAppDeployment";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { useToasts } from "./useToast";
import { useWriterTracking } from "@/composables/useWriterTracking";
import BuilderHeaderConnected from "./BuilderHeaderConnected.vue";
import BuilderHeaderMoreDropdown from "./BuilderHeaderMoreDropdown.vue";
import { useClipboard } from "@vueuse/core";
import { useSyncHealth } from "./useSyncHealth";

const wf = inject(injectionKeys.core);

const isStateExplorerShown = ref(false);
const isInviteCollaboratorsShown = ref(false);

const tracking = useWriterTracking(wf);
const toasts = useToasts();
const clipboard = useClipboard();
const { stateDotState, syncHealthStatus } = useSyncHealth(wf);

const {
	canDeploy,
	isDeploying,
	publishApplication,
	hasBeenPublished,
	lastDeployedAt,
	writerDeployUrl,
	name: applicationName,
} = useWriterAppDeployment(wf);

const dateFormater = new Intl.DateTimeFormat(undefined, {
	weekday: "long",
	year: "numeric",
	month: "long",
	day: "numeric",
	hour: "numeric",
	minute: "numeric",
});

async function requestDeployment() {
	tracking.track("nav_deploy_clicked");
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

function showStateExplorer() {
	tracking.track("nav_state_explorer_opened");
	isStateExplorerShown.value = true;
}

function showInviteCollaborators() {
	isInviteCollaboratorsShown.value = true;
}

async function copyInviteCollaboratorsURL() {
	try {
		await clipboard.copy(location.href);
	} catch {
		toasts.pushToast({ type: "error", message: "Could not copy link." });
	}
}
</script>

<style scoped>
.BuilderHeader {
	background: var(--wdsColorBlack);
	color: var(--builderBackgroundColor);
	padding: 0 12px 0 10px;
	display: grid;
	grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
	align-items: center;
	gap: 16px;
	padding-top: 1px;
	border-bottom: 1px solid var(--builderAreaSeparatorColor);
}

.BuilderHeader__logo {
	display: flex;
	align-items: center;
	gap: 6px;
}

.BuilderHeader__logo a {
	text-decoration: none;
	display: inline-flex;
	align-items: center;
}
.BuilderHeader__logo__appTitle {
	background-color: transparent;
	width: 100%;
	border: none;
	font-weight: 500;
	font-size: 16px;
	border-radius: 4px;
	padding: 4px;
	height: 32px;
	text-overflow: ellipsis;
}
.BuilderHeader__logo__appTitle:focus {
	outline: none;
}
.BuilderHeader__logo__appTitle:not([disabled]):hover,
.BuilderHeader__logo__appTitle:not([disabled]):focus {
	outline: none;
	background-color: var(--wdsColorGray5);
}

.BuilderHeader__toolbar {
	display: flex;
	align-items: center;
	justify-content: flex-end;
	gap: 8px;
}
.BuilderHeader__toolbar__deployBtn {
	text-wrap: nowrap;
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
	display: block;
}
.BuilderHeader hr {
	border: none;
	border-left: 1px solid var(--wdsColorGray6);
	height: 26px;
}

.BuilderHeader__toolbar__deployModal__text {
	font-size: 14px;
}

.BuilderHeader img {
	width: 32px;
}

button {
	background: unset;
	color: var(--builderBackgroundColor);
}
</style>
