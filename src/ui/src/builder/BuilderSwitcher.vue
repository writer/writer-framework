<template>
	<div class="BuilderSwitcher">
		<button
			data-automation-action="set-mode-ui"
			:class="{ active: activeId == 'ui' }"
			type="button"
			@click="selectOption('ui')"
		>
			<WdsIcon name="frame" />
			Interface
		</button>
		<button
			data-automation-action="set-mode-blueprints"
			:class="{ active: activeId == 'blueprints' }"
			type="button"
			@click="selectOption('blueprints')"
		>
			<WdsIcon name="wds-blueprints" />
			Blueprints
		</button>
		<button
			v-if="wf.isWriterCloudApp.value"
			:class="{ active: activeId == 'vault' }"
			data-automation-action="set-mode-vault"
			type="button"
			@click="selectOption('vault')"
		>
			<WdsIcon name="key-round" />
			Vault
		</button>
		<button
			:class="{ active: activeId == 'preview' }"
			data-automation-action="set-mode-preview"
			type="button"
			@click="selectOption('preview')"
		>
			<WdsIcon name="view" />
			Preview
		</button>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, Ref, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useWriterTracking } from "@/composables/useWriterTracking";
import WdsIcon from "@/wds/WdsIcon.vue";
import type { BuilderManagerMode } from "./builderManager";
import { Component } from "@/writerTypes";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

let selectedId: Ref<string> = ref(null);

const tracking = useWriterTracking(wf);

const previousActivePage: Record<"ui" | "blueprints", Component["id"]> = {
	ui: undefined,
	blueprints: undefined,
};

function canHaveActivePage(mode: BuilderManagerMode) {
	return mode === "blueprints" || mode === "ui";
}

function selectOption(optionId: BuilderManagerMode) {
	const preMode = wfbm.mode.value;
	if (preMode == optionId) return;

	if (canHaveActivePage(preMode) && wf.activePageId.value) {
		previousActivePage[preMode] = wf.activePageId.value;
	}

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

	wfbm.mode.value = optionId;

	// restore the previous active page
	if (
		canHaveActivePage(optionId) &&
		previousActivePage[optionId] &&
		wf.getComponentById(previousActivePage[optionId])
	) {
		wf.setActivePageId(previousActivePage[optionId]);
	}

	if (
		optionId == "preview" ||
		preMode == "blueprints" ||
		optionId == "blueprints"
	) {
		wfbm.setSelection(null);
	}
}

const activeId = computed(() => wfbm.getMode());
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
	gap: 10px;
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
