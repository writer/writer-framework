<template>
	<div
		v-if="ssbm.selectionStatus.value !== SelectionStatus.None"
		class="BuilderSettings"
		:class="{
			'BuilderSettings--collapsed': collapsed,
		}"
	>
		<div
			v-if="ssbm.isSingleSelectionActive.value"
			class="BuilderSettings__collapser"
		>
			<WdsButton
				v-if="collapsed"
				class="BuilderSettings__collapser__btn"
				size="smallIcon"
				variant="neutral"
				data-writer-tooltip-placement="left"
				data-writer-tooltip="Expand settings"
				data-automation-action="expand-settings"
				@click="toggleSettings"
			>
				<WdsIcon name="settings" />
			</WdsButton>
			<WdsButton
				v-else
				class="BuilderSettings__collapser__btn"
				size="smallIcon"
				variant="neutral"
				data-writer-tooltip-placement="left"
				data-writer-tooltip="Collapse settings"
				data-automation-action="collapse-settings"
				@click="toggleSettings"
			>
				<WdsIcon name="arrow-right-to-line" />
			</WdsButton>
		</div>
		<div
			v-if="ssbm.isSingleSelectionActive"
			class="BuilderSettings__titleBar"
		>
			<p class="BuilderSettings__titleBar__title">
				{{ componentDefinition.name }}
			</p>
			<div class="BuilderSettings__titleBar__actions">
				<WdsButton
					v-if="resultId"
					size="smallIcon"
					variant="neutral"
					data-writer-tooltip-placement="bottom"
					:data-writer-tooltip="
						isComponentIdCopied ? 'Copied!' : 'Copy result variable'
					"
					@click.prevent="copyComponentId"
				>
					<WdsIcon name="at-sign" />
				</WdsButton>
				<SharedMoreDropdown
					data-automation-action="settings-actions-dropdown"
					:options="dropdownOptions"
					trigger-custom-size="32px"
					trigger-icon="ellipsis-vertical"
					@select="handleDropdownSelect"
				/>
			</div>
		</div>
		<div
			v-if="ssbm.selectionStatus.value === SelectionStatus.Multiple"
			class="BuilderSettings__selectionCount"
			data-writer-tooltip-placement="left"
			:data-writer-tooltip="`${selectionCount} components selected`"
		>
			<p>{{ selectionCount }}</p>
		</div>
		<BuilderSettingsActions
			v-if="
				collapsed &&
				ssbm.selectionStatus.value === SelectionStatus.Multiple
			"
			class="BuilderSettings__actions"
		/>
		<BuilderSettingsMain class="BuilderSettings__main" :inert="collapsed" />
		<BuilderSettingsAddComponentModal
			v-if="ssbm.isSingleSelectionActive.value"
			v-model:is-open="isAddModalOpen"
			:selected-id="ssbm.firstSelectedId.value"
		/>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, watch, ref } from "vue";
import injectionKeys from "@/injectionKeys";

import BuilderSettingsMain from "./BuilderSettingsMain.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { SelectionStatus } from "../builderManager";
import { useButtonClipboard } from "../useButtonClipboard";
import { COMPONENT_TYPES_PAGE } from "@/constants/component";
import SharedMoreDropdown from "@/components/shared/SharedMoreDropdown.vue";
import { useWriterTracking } from "@/composables/useWriterTracking";
import BuilderSettingsActions from "./BuilderSettingsActions.vue";
import {
	BuilderSettingsDropdownActions,
	useBuilderSettingsActions,
} from "./useBuilderSettingsActions";
import BuilderSettingsAddComponentModal from "./BuilderSettingsAddComponentModal.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);

const resultId = computed(() => {
	const componentType = component.value?.type;

	const hasResultId =
		componentType &&
		!COMPONENT_TYPES_PAGE.has(componentType) &&
		component.value?.type.startsWith("blueprints_") &&
		componentDefinition.value?.outs?.["success"] !== undefined;

	return hasResultId ? `@{results.${component.value.id}}` : "";
});

const { copyText: copyComponentId, isCopied: isComponentIdCopied } =
	useButtonClipboard(resultId);

const tracking = useWriterTracking(wf);

const isAddModalOpen = ref(false);

const { dropdownOptions, handleDropdownSelect } = useBuilderSettingsActions(
	wf,
	ssbm,
	tracking,
	{
		[BuilderSettingsDropdownActions.Add]: () =>
			(isAddModalOpen.value = true),
	},
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
	grid-template-rows: min-content 0 auto;
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

.BuilderSettings__selectionCount {
	background-color: var(--wdsColorBlue3);
	color: var(--wdsColorBlue5);
	font-weight: 700;
	font-size: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.BuilderSettings__collapser {
	grid-row: 1;
	grid-column: 1;
	padding: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--builderSubtleSeparatorColor);
}

.BuilderSettings__collapser__btn:focus {
	border: 1px solid var(--builderSeparatorColor);
}

.BuilderSettings__titleBar {
	grid-row: 1;
	grid-column: 2;
	z-index: 2;
	display: grid;
	grid-template-columns: 1fr auto;
	gap: 8px;
	align-items: center;
	padding-right: 12px;
	background: var(--builderSubtleSeparatorColor);
}
.BuilderSettings__titleBar__actions {
	display: flex;
	align-items: center;
	gap: 8px;
}

.BuilderSettings__titleBar__title {
	margin: 0;
	padding: 12px 0 12px 0;
	font-family: Poppins;
	font-size: 16px;
	font-weight: 500;
	line-height: 140%;
	flex: 1 0 auto;
	text-wrap: wrap;
	max-width: 280px;
}

.BuilderSettings__actions {
	grid-row: 3;
	grid-column: 1;
	max-height: 320px;
	overflow-y: auto;
}

.BuilderSettings__main {
	width: 332px;
	grid-row: 3;
	grid-column: 1 / -1;
	overflow-x: hidden;
	overflow-y: auto;
	margin-top: 0;
	transition: 0.2s margin linear;
}

.BuilderSettings--collapsed .BuilderSettings__collapser {
	background: var(--wdsColorGray2);
}

.BuilderSettings--collapsed .BuilderSettings__main {
	overflow: hidden;
	max-height: 400px;
	margin-top: -400px;
	grid-column: 2;
}
</style>
