<template>
	<div class="BuilderSwitcher">
		<button
			data-automation-action="set-mode-ui"
			:class="{ active: activeId == 'ui' }"
			type="button"
			@click="selectOption('ui')"
		>
			<i class="icon material-symbols-outlined">{{
				BUILDER_MANAGER_MODE_ICONS.ui
			}}</i>
			Interface
		</button>
		<button
			data-automation-action="set-mode-blueprints"
			:class="{ active: activeId == 'blueprints' }"
			type="button"
			@click="selectOption('blueprints')"
		>
			<i class="icon material-symbols-outlined">{{
				BUILDER_MANAGER_MODE_ICONS.blueprints
			}}</i>
			Blueprints
		</button>
		<button
			:class="{ active: activeId == 'preview' }"
			data-automation-action="set-mode-preview"
			type="button"
			@click="selectOption('preview')"
		>
			<i class="icon material-symbols-outlined">{{
				BUILDER_MANAGER_MODE_ICONS.preview
			}}</i>
			Preview
		</button>
		<button
			v-if="wf.isWriterCloudApp.value && wf.featureFlags.value.includes('vault')"
			:class="{ active: activeId == 'vault' }"
			data-automation-action="set-mode-vault"
			type="button"
			@click="selectOption('vault')"
		>
			<i class="icon material-symbols-outlined">{{
				BUILDER_MANAGER_MODE_ICONS.vault
			}}</i>
			Vault
		</button>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, Ref, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { BUILDER_MANAGER_MODE_ICONS } from "@/constants/icons";
import type { BuilderManagerMode } from "./builderManager";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

let selectedId: Ref<string> = ref(null);

const tracking = useWriterTracking(wf);

const selectOption = (optionId: BuilderManagerMode) => {
	const preMode = ssbm.getMode();
	if (preMode == optionId) return;
	selectedId.value = optionId;
	switch (optionId) {
		case "ui":
			tracking.track("nav_ui_opened");
			break;
		case "preview":
			tracking.track("nav_preview_opened");
			break;
		case "blueprints":
			tracking.track("nav_blueprints_opened");
			break;
		case "vault":
			tracking.track("nav_vault_opened");
			break;
	}
	ssbm.mode.value = optionId;
	if (
		optionId == "preview" ||
		preMode == "blueprints" ||
		optionId == "blueprints"
	) {
		ssbm.setSelection(null);
	}
};

const activeId = computed(() => ssbm.getMode());
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSwitcher {
	display: flex;
	align-items: center;
	gap: 8px;
	overflow: hidden;
}

.BuilderSwitcher button {
	background-color: transparent;
	color: white;
	border: none;

	font-size: 14px;

	padding: 4px 12px 4px 12px;
	cursor: pointer;
	display: flex;
	align-items: center;
	gap: 4px;
	height: 32px;
	border-radius: 4px;
}
.BuilderSwitcher button:hover {
	background: var(--wdsColorGray5);
}

.BuilderSwitcher .icon {
	margin-right: 8px;
}

.BuilderSwitcher .active {
	background: var(--wdsColorGray6);
}
</style>
