<template>
	<div class="BuilderSettingsActions" :data-writer-id="selectedId">
		<WdsButton
			v-if="ssbm.selectionStatus.value === SelectionStatus.Multiple"
			class="BuilderSettingsActions__btn"
			variant="neutral"
			size="small"
			data-automation-action="clear-selection"
			data-writer-tooltip="Clear selection"
			data-writer-tooltip-placement="left"
			@click="ssbm.setSelection(null)"
		>
			<i class="material-symbols-outlined">close</i>
		</WdsButton>
		<WdsButton
			class="BuilderSettingsActions__btn BuilderSettingsActions__btn--delete"
			variant="neutral"
			size="small"
			data-automation-action="delete"
			data-writer-tooltip="Delete (Del)"
			data-writer-tooltip-placement="left"
			:disabled="isDeleteDisabled"
			@click="deleteSelectedComponents"
		>
			<i class="material-symbols-outlined">delete</i>
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import { SelectionStatus } from "../builderManager";
import { useWriterTracking } from "@/composables/useWriterTracking";
import {
	BuilderSettingsDropdownActions,
	useBuilderSettingsActions,
} from "./useBuilderSettingsActions";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const tracking = useWriterTracking(wf);

const { dropdownOptions, handleDropdownSelect } = useBuilderSettingsActions(
	wf,
	ssbm,
	tracking,
);

function deleteSelectedComponents() {
	handleDropdownSelect(BuilderSettingsDropdownActions.Delete);
}

const isDeleteDisabled = computed(() => {
	const option = dropdownOptions.value.find(
		(o) => o.value === BuilderSettingsDropdownActions.Delete,
	);
	if (!option) return true;
	return option.disabled;
});

const selectedId = ssbm.firstSelectedId;
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsActions {
	display: flex;
	flex-direction: column;
	align-items: center;
	background: var(--builderBackgroundColor);
	pointer-events: auto;
	overflow: hidden;
	justify-content: space-between;
	height: 100%;
	padding: 8px;
	width: 50px;
	transition: 0.2s gap linear;
	gap: 0;
}

.BuilderSettingsActions__btn {
	min-height: 32px;
}

.BuilderSettingsActions__btn--delete:not([disabled]) {
	color: var(--builderErrorColor);
}
</style>
