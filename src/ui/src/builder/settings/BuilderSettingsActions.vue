<template>
	<div
		class="BuilderSettingsActions"
		:class="{
			collapsed: ssbm.isSettingsBarCollapsed.value,
		}"
		:data-writer-id="selectedId"
	>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			data-writer-tooltip="Add child"
			data-writer-tooltip-placement="left"
			variant="neutral"
			size="smallIcon"
			class="actionButton"
			:disabled="!shortcutsInfo?.isAddEnabled"
			@click="
				shortcutsInfo?.isAddEnabled
					? (isAddModalOpen = true)
					: undefined
			"
			><i class="material-symbols-outlined">add</i></WdsButton
		>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			class="actionButton"
			size="small"
			variant="neutral"
			data-writer-tooltip-placement="left"
			:data-writer-tooltip="`Move up (${getModifierKeyName()}↑)`"
			:disabled="!shortcutsInfo?.isMoveUpEnabled"
			@click="
				shortcutsInfo?.isMoveUpEnabled
					? moveComponentUp(selectedId)
					: undefined
			"
			><i class="material-symbols-outlined">arrow_upward</i></WdsButton
		>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			class="actionButton"
			variant="neutral"
			size="small"
			:data-writer-tooltip="`Move down (${getModifierKeyName()}↓)`"
			data-writer-tooltip-placement="left"
			:disabled="!shortcutsInfo?.isMoveDownEnabled"
			@click="
				shortcutsInfo?.isMoveDownEnabled
					? moveComponentDown(selectedId)
					: undefined
			"
		>
			<i class="material-symbols-outlined">arrow_downward</i>
		</WdsButton>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			class="actionButton"
			variant="neutral"
			size="small"
			:data-writer-tooltip="`Cut (${getModifierKeyName()}X)`"
			data-writer-tooltip-placement="left"
			:disabled="!shortcutsInfo?.isCutEnabled"
			@click="
				shortcutsInfo?.isCutEnabled
					? cutComponent(selectedId)
					: undefined
			"
		>
			<i class="material-symbols-outlined">cut</i>
		</WdsButton>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			class="actionButton"
			variant="neutral"
			size="small"
			:data-writer-tooltip="`Copy (${getModifierKeyName()}C)`"
			data-writer-tooltip-placement="left"
			:disabled="!shortcutsInfo?.isCopyEnabled"
			@click="
				shortcutsInfo?.isCopyEnabled
					? copyComponent(selectedId)
					: undefined
			"
		>
			<i class="material-symbols-outlined">content_copy</i>
		</WdsButton>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			class="actionButton"
			variant="neutral"
			size="small"
			:data-writer-tooltip="`Paste (${getModifierKeyName()}V)`"
			data-writer-tooltip-placement="left"
			:disabled="!isPasteEnabled"
			@click="handlePasteComponent"
		>
			<i class="material-symbols-outlined">content_paste</i>
		</WdsButton>
		<WdsButton
			v-if="ssbm.isSingleSelectionActive.value"
			class="actionButton"
			variant="neutral"
			size="small"
			:data-writer-tooltip="`Go to parent (${getModifierKeyName()}⇧↑)`"
			data-writer-tooltip-placement="left"
			:disabled="!shortcutsInfo?.isGoToParentEnabled"
			@click="
				shortcutsInfo?.isGoToParentEnabled
					? goToParent(selectedId, selectedInstancePath)
					: undefined
			"
		>
			<i class="material-symbols-outlined">move_up</i>
		</WdsButton>
		<WdsButton
			v-if="ssbm.selectionStatus.value === SelectionStatus.Multiple"
			class="actionButton"
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
			class="actionButton delete"
			variant="neutral"
			size="small"
			data-automation-action="delete"
			data-writer-tooltip="Delete (Del)"
			data-writer-tooltip-placement="left"
			:disabled="!shortcutsInfo?.isDeleteEnabled"
			@click="deleteSelectedComponents"
		>
			<i class="material-symbols-outlined">delete</i>
		</WdsButton>

		<WdsModal
			v-if="isAddModalOpen"
			title="Add child component"
			display-close-button
			@close="isAddModalOpen = false"
		>
			<input
				class="addModalInput"
				type="text"
				list="validChildrenTypes"
				placeholder="Component..."
				@change="addComponent"
			/>
			<datalist id="validChildrenTypes">
				<option
					v-for="(definition, type) in validChildrenTypes"
					:key="type"
					:value="definition.name"
				>
					{{ definition.name }}
				</option>
			</datalist>
		</WdsModal>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, Ref, ref, watch } from "vue";
import { useComponentActions } from "../useComponentActions";
import { WriterComponentDefinition } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { getModifierKeyName } from "@/core/detectPlatform";
import WdsButton from "@/wds/WdsButton.vue";
import WdsModal from "@/wds/WdsModal.vue";
import { SelectionStatus } from "../builderManager";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { useToasts } from "../useToast";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const tracking = useWriterTracking(wf);

const {
	createAndInsertComponent,
	moveComponentUp,
	moveComponentDown,
	cutComponent,
	pasteComponent,
	copyComponent,
	isAddAllowed,
	isCopyAllowed,
	isCutAllowed,
	isGoToParentAllowed,
	isPasteAllowed,
	isDeleteAllowed,
	getEnabledMoves,
	removeComponentsSubtree,
	goToParent,
} = useComponentActions(wf, ssbm, tracking);

const toasts = useToasts();

async function handlePasteComponent() {
	try {
		await pasteComponent(selectedId.value);
	} catch (error) {
		toasts.pushToast({ type: "error", message: String(error) });
	}
}

function deleteSelectedComponents() {
	if (!shortcutsInfo.value.isDeleteEnabled) return;
	const componentIds = ssbm.selection.value.map((c) => c.componentId);
	if (componentIds.length === 0) return;
	removeComponentsSubtree(...componentIds);
}

const selectedId = ssbm.firstSelectedId;
const selectedInstancePath = computed(
	() => ssbm.firstSelectedItem.value?.instancePath,
);

const isAddModalOpen = ref(false);

const shortcutsInfo: Ref<{
	componentTypeName: string;
	toolkit?: WriterComponentDefinition["toolkit"];
	isAddEnabled: boolean;
	isMoveUpEnabled: boolean;
	isMoveDownEnabled: boolean;
	isCopyEnabled: boolean;
	isCutEnabled: boolean;
	isGoToParentEnabled: boolean;
	isDeleteEnabled: boolean;
}> = ref(null);

const isPasteEnabled = computed(() => {
	if (!ssbm.firstSelectedId.value) return false;
	return isPasteAllowed(ssbm.firstSelectedId.value);
});

const validChildrenTypes = computed(() => {
	const types = wf.getContainableTypes(selectedId.value);
	const result: Record<string, WriterComponentDefinition> = {};

	types.map((type) => {
		const definition = wf.getComponentDefinition(type);
		result[type] = definition;
	});

	return result;
});

function addComponent(event: Event) {
	const definitionName = (event.target as HTMLInputElement).value;
	const matchingTypes = Object.entries(validChildrenTypes.value).filter(
		([_, definition]) => {
			if (definition.name == definitionName) return true;
			return false;
		},
	);
	if (matchingTypes.length == 0) return;
	const type = matchingTypes[0][0];
	createAndInsertComponent(type, selectedId.value);
	isAddModalOpen.value = false;
}

function reprocessShorcutsInfo(): void {
	const component = wf.getComponentById(selectedId.value);
	if (!component) return;
	const { up: isMoveUpEnabled, down: isMoveDownEnabled } = getEnabledMoves(
		selectedId.value,
	);
	shortcutsInfo.value = {
		isAddEnabled: isAddAllowed(selectedId.value),
		componentTypeName: wf.getComponentDefinition(component.type)?.name,
		toolkit: wf.getComponentDefinition(component.type)?.toolkit,
		isMoveUpEnabled,
		isMoveDownEnabled,
		isCopyEnabled: isCopyAllowed(selectedId.value),
		isCutEnabled: isCutAllowed(selectedId.value),
		isGoToParentEnabled: isGoToParentAllowed(selectedId.value),
		isDeleteEnabled: isDeleteAllowed(selectedId.value),
	};
}

watch(
	() => wf.getComponentById(selectedId.value)?.position,
	async (newPosition) => {
		if (typeof newPosition == "undefined" || newPosition === null) return;
		reprocessShorcutsInfo();
	},
	{ flush: "post" },
);

onMounted(() => {
	reprocessShorcutsInfo();
});
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
}

.BuilderSettingsActions.collapsed {
	gap: 0;
}

.type {
	display: flex;
	align-items: center;
	padding-left: 16px;
	padding-right: 16px;
	height: 36px;
	background: var(--builderSelectedColor);
}

.actionButton:not([disabled]).delete {
	color: var(--builderErrorColor);
}

.addModalInput {
	outline: none;
	border: 1px solid var(--builderSeparatorColor);
	width: 100%;
	border-radius: 8px;
	padding: 8px;
}
</style>
