<template>
	<div
		v-if="ssbm.isSelectionActive()"
		class="BuilderSettings"
		:class="{ collapsed, miniDocsActive }"
	>
		<div class="collapser">
			<WdsButton
				v-if="collapsed"
				class="collapserButton"
				size="small"
				variant="neutral"
				data-writer-tooltip-placement="left"
				data-writer-tooltip="Expand settings"
				@click="toggleSettings"
				><i class="material-symbols-outlined">settings</i></WdsButton
			>
			<WdsButton
				v-else
				class="collapserButton"
				size="small"
				variant="neutral"
				data-writer-tooltip-placement="left"
				data-writer-tooltip="Collapse settings"
				@click="toggleSettings"
				><i class="material-symbols-outlined"
					>double_arrow</i
				></WdsButton
			>
		</div>
		<div class="titleBar">
			<div>{{ componentDefinition.name }}</div>
			<WdsButton
				v-if="Boolean(rawMiniDocs)"
				:inert="collapsed"
				class="collapserButton"
				size="small"
				variant="neutral"
				data-writer-tooltip-placement="top"
				data-writer-tooltip="Toggle mini docs"
				@click="toggleMiniDocs"
				><i class="material-symbols-outlined">info</i></WdsButton
			>
		</div>
		<BuilderSettingsMiniDocs
			v-if="miniDocsActive && rawMiniDocs && !collapsed"
			class="miniDocs"
			:raw-mini-docs="rawMiniDocs"
		></BuilderSettingsMiniDocs>
		<BuilderSettingsActions class="actions"></BuilderSettingsActions>
		<BuilderSettingsMain
			:inert="collapsed"
			class="main"
		></BuilderSettingsMain>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";

import BuilderSettingsActions from "./BuilderSettingsActions.vue";
import BuilderSettingsMain from "./BuilderSettingsMain.vue";
import BuilderSettingsMiniDocs from "./BuilderSettingsMiniDocs.vue";
import WdsButton from "@/wds/WdsButton.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const miniDocsActive = ref(false);

const component = computed(() => wf.getComponentById(ssbm.getSelectedId()));
const collapsed = computed(() => ssbm.isSettingsBarCollapsed.value);

function toggleSettings() {
	ssbm.isSettingsBarCollapsed.value = !ssbm.isSettingsBarCollapsed.value;
}

const componentDefinition = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition;
});

const rawMiniDocs = computed(() => componentDefinition.value?.docs?.trim());

watch(component, (newComponent) => {
	if (!newComponent) ssbm.setSelection(null);
});

const toggleMiniDocs = () => {
	miniDocsActive.value = !miniDocsActive.value;
};
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettings {
	display: grid;
	grid-template-columns: 50px min-content;
	grid-template-rows: min-content auto;
	overflow: hidden;
	background: var(--builderBackgroundColor);
	position: absolute;
	transition:
		0.2s margin,
		height linear;
	right: 24px;
	bottom: 20px;
	z-index: 4;
	width: fit-content;
	overflow: hidden;
	border-width: 1px solid var(--builderAreaSeparatorColor);
	background: var(--builderBackgroundColor);
	box-shadow: 0px 3px 40px 0px rgba(172, 185, 220, 0.4);
	border-radius: 12px;
	top: v-bind("ssbm.getMode() == `workflows` ? `72px` : `20px`");
}

.BuilderSettings.collapsed {
	margin-right: -357px;
	max-height: 340px;
}

.BuilderSettings:not(.miniDocsActive) {
	grid-template-rows: min-content 0 auto;
}

.collapser {
	grid-row: 1;
	grid-column: 1;
	padding: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--builderSubtleSeparatorColor);
}

.collapserButton {
	height: 34px;
	width: 34px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
}

.titleBar {
	grid-row: 1;
	grid-column: 2;
	z-index: 2;
	display: flex;
	align-items: center;
	padding-right: 12px;
	overflow: hidden;
	background: var(--builderSubtleSeparatorColor);
}

.titleBar > div {
	padding: 12px 0 12px 0;
	font-family: Poppins;
	font-size: 16px;
	font-weight: 500;
	line-height: 140%;
	flex: 1 0 auto;
	text-wrap: wrap;
	max-width: 280px;
}

.miniDocs {
	grid-row: 2;
	grid-column: 1 / 3;
	background: var(--builderSubtleSeparatorColor);
	padding: 0 24px 24px 24px;
	overflow: auto;
}

.actions {
	grid-row: 3;
	grid-column: 1;
	max-height: 320px;
	overflow-y: auto;
}

.main {
	width: 332px;
	grid-row: 3;
	grid-column: 2;
	border-left: 1px solid var(--builderSeparatorColor);
	overflow-x: hidden;
	overflow-y: auto;
	margin-top: 0;
	transition: 0.2s margin linear;
}

.BuilderSettings.collapsed .main {
	overflow: hidden;
	max-height: 400px;
	margin-top: -400px;
}

.docs {
	font-size: 0.75rem;
	padding: 24px;
	line-height: 1.5;
	background: var(--builderSubtleHighlightColorSolid);
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	white-space: pre-wrap;
}

.docs div:not(:first-child) {
	margin-top: 16px;
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	padding-top: 16px;
}

.sections {
	background: var(--builderBackgroundColor);
}

.sections[inert] {
	opacity: 0.7;
}

.sections > *:not(:first-child) {
	border-top: 1px solid var(--builderSeparatorColor);
}

.debug {
	color: var(--builderSecondaryTextColor);
	border-top: 1px solid var(--builderSeparatorColor);
	padding: 24px;
}

.warning {
	display: flex;
	align-items: center;
	background: var(--builderWarningColor);
	color: var(--builderWarningTextColor);
	border-radius: 4px;
	gap: 12px;
	margin: 12px 12px 0;
	padding: 12px;
}
</style>
