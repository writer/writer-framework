import { computed } from "vue";
import { useComponentActions } from "../useComponentActions";
import { Core, BuilderManager } from "@/writerTypes";
import { getModifierKeyName } from "@/core/detectPlatform";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { useToasts } from "../useToast";
import { Option } from "@/components/shared/SharedMoreDropdown.vue";

export enum BuilderSettingsDropdownActions {
	Add = "add",
	MoveUp = "moveUp",
	MoveDown = "moveDown",
	Cut = "cut",
	Copy = "copy",
	Paste = "paste",
	GoToParent = "goToParent",
	Delete = "delete",
}

export function useBuilderSettingsActions(
	wf: Core,
	ssbm: BuilderManager,
	tracking?: ReturnType<typeof useWriterTracking>,
	callbacks: Partial<Record<BuilderSettingsDropdownActions, () => void>> = {},
) {
	const {
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

	const selectedId = ssbm.firstSelectedId;
	const selectedInstancePath = computed(
		() => ssbm.firstSelectedItem.value?.instancePath,
	);

	const shortcutsInfo = computed(() => {
		const component = wf.getComponentById(selectedId.value);
		if (!component) return {};
		const { up: isMoveUpEnabled, down: isMoveDownEnabled } =
			getEnabledMoves(selectedId.value);
		return {
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
	});

	const isPasteEnabled = computed(() => {
		if (!ssbm.firstSelectedId.value) return false;
		return isPasteAllowed(ssbm.firstSelectedId.value);
	});

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

	const dropdownOptions = computed(() => {
		const options: Option[] = [
			{
				value: BuilderSettingsDropdownActions.Add,
				label: "Add child",
				icon: "add",
				disabled: !shortcutsInfo.value.isAddEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.MoveUp,
				label: `Move up`,
				shortcut: `${getModifierKeyName()}↑`,
				icon: "arrow_upward",
				disabled: !shortcutsInfo.value.isMoveUpEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.MoveDown,
				label: `Move down`,
				shortcut: `${getModifierKeyName()}↓`,
				icon: "arrow_downward",
				disabled: !shortcutsInfo.value.isMoveDownEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Cut,
				label: `Cut`,
				shortcut: `${getModifierKeyName()}X`,
				icon: "cut",
				disabled: !shortcutsInfo.value.isCutEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Copy,
				label: `Copy`,
				shortcut: `${getModifierKeyName()}C`,
				icon: "content_copy",
				disabled: !shortcutsInfo.value.isCopyEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Paste,
				label: `Paste`,
				shortcut: `${getModifierKeyName()}V`,
				icon: "content_paste",
				disabled: !isPasteEnabled.value,
			},
			{
				value: BuilderSettingsDropdownActions.GoToParent,
				label: `Go to parent`,
				shortcut: `${getModifierKeyName()}⇧↑`,
				icon: "move_up",
				disabled: !shortcutsInfo.value.isGoToParentEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Delete,
				label: "Delete",
				shortcut: "Del",
				icon: "delete",
				variant: "danger",
				disabled: !shortcutsInfo.value.isDeleteEnabled,
			},
		];

		return options;
	});

	function handleDropdownSelect(selected: BuilderSettingsDropdownActions) {
		switch (selected) {
			case BuilderSettingsDropdownActions.Add:
				// Handled by callback
				break;
			case BuilderSettingsDropdownActions.MoveUp:
				moveComponentUp(selectedId.value);
				break;
			case BuilderSettingsDropdownActions.MoveDown:
				moveComponentDown(selectedId.value);
				break;
			case BuilderSettingsDropdownActions.Cut:
				cutComponent(selectedId.value);
				break;
			case BuilderSettingsDropdownActions.Copy:
				copyComponent(selectedId.value);
				break;
			case BuilderSettingsDropdownActions.Paste:
				handlePasteComponent();
				break;
			case BuilderSettingsDropdownActions.GoToParent:
				goToParent(selectedId.value, selectedInstancePath.value);
				break;
			case BuilderSettingsDropdownActions.Delete:
				deleteSelectedComponents();
				break;
		}

		callbacks[selected]?.();
	}

	return {
		dropdownOptions,
		handleDropdownSelect,
	};
}
