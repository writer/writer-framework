import { computed, MaybeRef, unref } from "vue";
import { useComponentActions } from "../useComponentActions";
import { Core, BuilderManager } from "@/writerTypes";
import { getModifierKeyName, isPlatformMac } from "@/core/detectPlatform";
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

export function isBuilderSettingsDropdownAction(
	value: unknown,
): value is BuilderSettingsDropdownActions {
	return (
		typeof value === "string" &&
		Object.values(BuilderSettingsDropdownActions).includes(
			value as BuilderSettingsDropdownActions,
		)
	);
}

/**
 * @param targetComponent specific the component that will be used for actions
 */
export function useBuilderSettingsActions(
	wf: Core,
	wfbm: BuilderManager,
	tracking?: ReturnType<typeof useWriterTracking>,
	callbacks: Partial<Record<BuilderSettingsDropdownActions, () => void>> = {},
	targetComponent?: MaybeRef<{ instancePath: string; componentId: string }>,
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
	} = useComponentActions(wf, wfbm, tracking);

	const toasts = useToasts();

	const componentId = computed(() => {
		return targetComponent
			? unref(targetComponent).componentId
			: wfbm.firstSelectedId.value;
	});
	const instancePath = computed(() => {
		return targetComponent
			? unref(targetComponent).instancePath
			: wfbm.firstSelectedItem.value.instancePath;
	});

	const shortcutsInfo = computed(() => {
		const component = wf.getComponentById(componentId.value);
		if (!component) return {};
		const { up: isMoveUpEnabled, down: isMoveDownEnabled } =
			getEnabledMoves(componentId.value);
		return {
			isAddEnabled: isAddAllowed(componentId.value),
			componentTypeName: wf.getComponentDefinition(component.type)?.name,
			toolkit: wf.getComponentDefinition(component.type)?.toolkit,
			isMoveUpEnabled,
			isMoveDownEnabled,
			isCopyEnabled: isCopyAllowed(componentId.value),
			isCutEnabled: isCutAllowed(componentId.value),
			isGoToParentEnabled: isGoToParentAllowed(componentId.value),
			isDeleteEnabled: isDeleteAllowed(componentId.value),
		};
	});

	const isPasteEnabled = computed(() => {
		if (!wfbm.firstSelectedId.value) return false;
		return isPasteAllowed(wfbm.firstSelectedId.value);
	});

	async function handlePasteComponent() {
		try {
			await pasteComponent(componentId.value);
		} catch (error) {
			toasts.pushToast({ type: "error", message: String(error) });
		}
	}

	function deleteComponent() {
		if (!shortcutsInfo.value.isDeleteEnabled) return;
		if (targetComponent) {
			removeComponentsSubtree(unref(targetComponent).componentId);
			return;
		}
		const componentIds = wfbm.selection.value.map((c) => c.componentId);
		if (componentIds.length === 0) return;
		removeComponentsSubtree(...componentIds);
	}

	const dropdownOptions = computed(() => {
		const options: Option[] = [
			{
				value: BuilderSettingsDropdownActions.Add,
				label: "Add child",
				icon: "plus",
				disabled: !shortcutsInfo.value.isAddEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.MoveUp,
				label: `Move up`,
				shortcut: `${getModifierKeyName()}↑`,
				icon: "arrow-up",
				disabled: !shortcutsInfo.value.isMoveUpEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.MoveDown,
				label: `Move down`,
				shortcut: `${getModifierKeyName()}↓`,
				icon: "arrow-down",
				disabled: !shortcutsInfo.value.isMoveDownEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Cut,
				label: `Cut`,
				shortcut: `${getModifierKeyName()}X`,
				icon: "scissors",
				disabled: !shortcutsInfo.value.isCutEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Copy,
				label: `Copy`,
				shortcut: `${getModifierKeyName()}C`,
				icon: "clipboard",
				disabled: !shortcutsInfo.value.isCopyEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Paste,
				label: `Paste`,
				shortcut: `${getModifierKeyName()}V`,
				icon: "clipboard-paste",
				disabled: !isPasteEnabled.value,
			},
			{
				value: BuilderSettingsDropdownActions.GoToParent,
				label: `View parent`,
				shortcut: `${getModifierKeyName()}⇧↑`,
				icon: "list-tree",
				disabled: !shortcutsInfo.value.isGoToParentEnabled,
			},
			{
				value: BuilderSettingsDropdownActions.Delete,
				label: "Delete",
				shortcut: isPlatformMac() ? "⌫" : "Del",
				icon: "trash-2",
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
				moveComponentUp(componentId.value);
				break;
			case BuilderSettingsDropdownActions.MoveDown:
				moveComponentDown(componentId.value);
				break;
			case BuilderSettingsDropdownActions.Cut:
				cutComponent(componentId.value);
				break;
			case BuilderSettingsDropdownActions.Copy:
				copyComponent(componentId.value);
				break;
			case BuilderSettingsDropdownActions.Paste:
				handlePasteComponent();
				break;
			case BuilderSettingsDropdownActions.GoToParent:
				goToParent(componentId.value, instancePath.value);
				break;
			case BuilderSettingsDropdownActions.Delete:
				deleteComponent();
				break;
		}

		callbacks[selected]?.();
	}

	return {
		dropdownOptions,
		handleDropdownSelect,
	};
}
