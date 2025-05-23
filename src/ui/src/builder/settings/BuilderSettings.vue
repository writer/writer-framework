<template>
	<div
		v-if="ssbm.selectionStatus.value !== SelectionStatus.None"
		class="BuilderSettings"
		:class="{
			'BuilderSettings--collapsed': collapsed,
			'BuilderSettings--miniDocActive': miniDocsActive,
		}"
	>
		<div v-if="ssbm.isSingleSelectionActive.value" class="collapser">
			<WdsButton
				v-if="collapsed"
				class="collapserButton"
				size="smallIcon"
				variant="neutral"
				data-writer-tooltip-placement="left"
				data-writer-tooltip="Expand settings"
				data-automation-action="expand-settings"
				@click="toggleSettings"
				><i class="material-symbols-outlined">settings</i></WdsButton
			>
			<WdsButton
				v-else
				class="collapserButton"
				size="smallIcon"
				variant="neutral"
				data-writer-tooltip-placement="left"
				data-writer-tooltip="Collapse settings"
				data-automation-action="collapse-settings"
				@click="toggleSettings"
				><i class="material-symbols-outlined"
					>double_arrow</i
				></WdsButton
			>
		</div>
		<div v-if="ssbm.isSingleSelectionActive" class="titleBar">
			<div>{{ componentDefinition.name }}</div>
		</div>
		<div
			v-if="ssbm.selectionStatus.value === SelectionStatus.Multiple"
			class="BuilderSettings__selectionCount"
			data-writer-tooltip-placement="left"
			:data-writer-tooltip="`${selectionCount} components selected`"
		>
			<p>{{ selectionCount }}</p>
		</div>
		<BuilderSettingsActions class="actions"></BuilderSettingsActions>
		<BuilderSettingsMain
			:inert="collapsed"
			class="main"
		></BuilderSettingsMain>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, ref, watch } from "vue";
import injectionKeys from "@/injectionKeys";

import BuilderSettingsActions from "./BuilderSettingsActions.vue";
import BuilderSettingsMain from "./BuilderSettingsMain.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { SelectionStatus } from "../builderManager";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const miniDocsActive = ref(false);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);

const collapsed = computed(() => {
	if (ssbm.selectionStatus.value === SelectionStatus.Multiple) return true;
	return ssbm.isSettingsBarCollapsed.value;
});

const selectionCount = computed(() => ssbm.selection.value.length);

function toggleSettings() {
	ssbm.isSettingsBarCollapsed.value = !ssbm.isSettingsBarCollapsed.value;
}

const componentDefinition = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition;
});

watch(component, (newComponent) => {
	if (!newComponent) ssbm.setSelection(null);
});
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
	box-shadow: var(--wdsShadowLarge);
	border-radius: 12px;
	top: v-bind("ssbm.getMode() == `blueprints` ? `82px` : `20px`");
}

.BuilderSettings--collapsed {
	margin-right: -357px;
	max-height: 340px;
	bottom: unset;
}

.BuilderSettings:not(.BuilderSettings--miniDocActive) {
	grid-template-rows: min-content 0 auto;
}

.BuilderSettings__selectionCount {
	background-color: var(--wdsColorBlue3);
	color: var(--wdsColorBlue5);
	font-weight: 700;
	font-size: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
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

.collapserButton:focus {
	border: 1px solid var(--builderSeparatorColor);
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

.BuilderSettings--collapsed .main {
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
