import { ref, computed, type Ref, onUnmounted } from "vue";
import type { BuilderManagerMode } from "../builderManager";
import { generateBuilderManager } from "../builderManager";

type BuilderManager = ReturnType<typeof generateBuilderManager>;

interface SelectionRectangle {
	isSelecting: boolean;
	startX: number;
	startY: number;
	left: number;
	top: number;
	width: number;
	height: number;
}

const MIN_SELECTION_SIZE_PX = 5;
const DRAG_SELECTION_CLICK_DELAY_MS = 100;
const MOVEMENT_THRESHOLD = 3;

interface UseDragToSelectOptions {
	wrapperRef: Ref<HTMLElement | null>;
	builderMode: Ref<BuilderManagerMode>;
	builderManager: BuilderManager;
	isAnnotating: Ref<boolean>;
	justCompletedDragSelection: Ref<boolean>;
}

export function useDragToSelect(options: UseDragToSelectOptions) {
	const {
		wrapperRef,
		builderMode,
		builderManager,
		isAnnotating,
		justCompletedDragSelection,
	} = options;

	const selectionRect = ref<SelectionRectangle>({
		isSelecting: false,
		startX: 0,
		startY: 0,
		left: 0,
		top: 0,
		width: 0,
		height: 0,
	});

	const dragAbortController = new AbortController();

	const isCursorSelecting = computed(() => selectionRect.value.isSelecting);

	const isHoveringSelectableArea = ref(false);

	function shouldAllowSelectionInBlueprints(target: HTMLElement): boolean {
		const targetEl = target.closest<HTMLElement>("[data-writer-id]");
		if (!targetEl) return true;

		const blueprintsBlueprint = target.closest<HTMLElement>(
			".BlueprintsBlueprint",
		);
		if (!blueprintsBlueprint) return false;

		if (targetEl === blueprintsBlueprint) return true;

		return false;
	}

	function isClickOnBlueprintsCanvas(target: HTMLElement): boolean {
		const blueprintsBlueprint = target.closest<HTMLElement>(
			".BlueprintsBlueprint",
		);
		if (!blueprintsBlueprint) return false;

		const nodeContainer =
			blueprintsBlueprint.querySelector<HTMLElement>(".nodeContainer");
		return nodeContainer ? nodeContainer.contains(target) : true;
	}

	function cleanupDragSelection() {
		if (!selectionRect.value.isSelecting) return;

		selectionRect.value.isSelecting = false;
		document.body.style.userSelect = "";
		document.body.style.cursor = "";
	}

	function updateSelectionRect(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) return;
		if (builderMode.value === "preview") return;

		const wrapper = wrapperRef.value;
		if (!wrapper) return;

		try {
			const wrapperRect = wrapper.getBoundingClientRect();
			const currentX = ev.clientX - wrapperRect.left;
			const currentY = ev.clientY - wrapperRect.top + wrapper.scrollTop;

			const { startX, startY } = selectionRect.value;
			const left = Math.min(startX, currentX);
			const top = Math.min(startY, currentY) - wrapper.scrollTop;
			const width = Math.abs(currentX - startX);
			const height = Math.abs(currentY - startY);

			selectionRect.value = {
				...selectionRect.value,
				left,
				top,
				width,
				height,
			};
		} catch {
			cleanupDragSelection();
		}
	}

	function handleDocumentMousemove(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) return;
		updateSelectionRect(ev);
		ev.preventDefault();
	}

	function handleMousedown(ev: MouseEvent) {
		if (builderMode.value === "preview") return;
		if (isAnnotating.value) return;

		if (ev.shiftKey || ev.ctrlKey || ev.metaKey) return;

		if (builderMode.value === "blueprints" && !ev.altKey) return;

		const target = ev.target as HTMLElement;

		const targetEl = target.closest<HTMLElement>("[data-writer-id]");
		if (targetEl) {
			if (builderMode.value === "blueprints") {
				if (!shouldAllowSelectionInBlueprints(target)) return;
			} else {
				return;
			}
		}

		const unselectableEl = target.closest<HTMLElement>(
			"[data-writer-unselectable]",
		);
		if (unselectableEl) return;

		if (target.classList.contains("selectionRectangle")) return;

		const wrapper = wrapperRef.value;
		if (!wrapper) return;

		if (!wrapper.contains(target)) return;

		if (builderMode.value === "blueprints") {
			if (!isClickOnBlueprintsCanvas(target)) return;
		}

		const wrapperRect = wrapper.getBoundingClientRect();
		const startX = ev.clientX - wrapperRect.left;
		const startY = ev.clientY - wrapperRect.top + wrapper.scrollTop;

		selectionRect.value = {
			isSelecting: true,
			startX,
			startY,
			left: startX,
			top: startY - wrapper.scrollTop,
			width: 0,
			height: 0,
		};

		document.body.style.userSelect = "none";
		document.body.style.cursor = "crosshair";

		document.addEventListener("mousemove", handleDocumentMousemove, {
			signal: dragAbortController.signal,
		});

		ev.stopPropagation();
		ev.preventDefault();
	}

	function handleMousemove(ev: MouseEvent) {
		if (selectionRect.value.isSelecting) {
			if (builderMode.value === "blueprints") {
				ev.stopPropagation();
			}
			updateSelectionRect(ev);
			ev.preventDefault();
			return;
		}

		if (builderMode.value === "preview") return;
		if (isAnnotating.value) return;

		if (ev.shiftKey || ev.ctrlKey || ev.metaKey) {
			isHoveringSelectableArea.value = false;
			return;
		}

		if (builderMode.value === "blueprints" && !ev.altKey) {
			isHoveringSelectableArea.value = false;
			return;
		}

		const target = ev.target as HTMLElement;
		const wrapper = wrapperRef.value;
		if (!wrapper || !wrapper.contains(target)) {
			isHoveringSelectableArea.value = false;
			return;
		}

		const targetEl = target.closest<HTMLElement>("[data-writer-id]");
		if (targetEl) {
			if (builderMode.value === "blueprints") {
				if (!shouldAllowSelectionInBlueprints(target)) {
					isHoveringSelectableArea.value = false;
					return;
				}
			} else {
				isHoveringSelectableArea.value = false;
				return;
			}
		}

		const unselectableEl = target.closest<HTMLElement>(
			"[data-writer-unselectable]",
		);
		if (unselectableEl || target.classList.contains("selectionRectangle")) {
			isHoveringSelectableArea.value = false;
			return;
		}

		if (builderMode.value === "blueprints") {
			if (!isClickOnBlueprintsCanvas(target)) {
				isHoveringSelectableArea.value = false;
				return;
			}
		}

		isHoveringSelectableArea.value = true;
	}

	function handleMouseup(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) return;
		if (builderMode.value === "preview") return;

		const { left, top, width, height } = selectionRect.value;

		if (width < MIN_SELECTION_SIZE_PX || height < MIN_SELECTION_SIZE_PX) {
			cleanupDragSelection();
			return;
		}

		const wrapper = wrapperRef.value;
		if (!wrapper) {
			cleanupDragSelection();
			return;
		}

		const wrapperRect = wrapper.getBoundingClientRect();
		const selectionRectAbsolute = {
			left: wrapperRect.left + left,
			top: wrapperRect.top + top,
			right: wrapperRect.left + left + width,
			bottom: wrapperRect.top + top + height,
		};

		const allComponentEls =
			wrapper.querySelectorAll<HTMLElement>("[data-writer-id]");
		const selectedComponents: Array<{
			componentId: string;
			instancePath: string;
		}> = [];

		for (const element of Array.from(allComponentEls)) {
			if (element.closest("[data-writer-unselectable]")) continue;

			const componentRect = element.getBoundingClientRect();

			if (
				componentRect.left >= selectionRectAbsolute.left &&
				componentRect.right <= selectionRectAbsolute.right &&
				componentRect.top >= selectionRectAbsolute.top &&
				componentRect.bottom <= selectionRectAbsolute.bottom
			) {
				const componentId = element.dataset.writerId;
				const instancePath = element.dataset.writerInstancePath;
				if (componentId) {
					selectedComponents.push({ componentId, instancePath });
				}
			}
		}

		if (selectedComponents.length > 0) {
			builderManager.setSelection(null);
			selectedComponents.forEach(({ componentId, instancePath }) => {
				builderManager.appendSelection(
					componentId,
					instancePath,
					"click",
				);
			});
			justCompletedDragSelection.value = true;
			setTimeout(() => {
				justCompletedDragSelection.value = false;
			}, DRAG_SELECTION_CLICK_DELAY_MS);
		} else {
			builderManager.setSelection(null);
		}

		cleanupDragSelection();

		ev.preventDefault();
		ev.stopPropagation();
		ev.stopImmediatePropagation();
	}

	function handleDocumentMouseup(ev: MouseEvent) {
		if (selectionRect.value.isSelecting) {
			const wrapper = wrapperRef.value;
			if (wrapper && wrapper.contains(ev.target as Node)) {
				return;
			}
			cleanupDragSelection();
		}
	}

	onUnmounted(() => {
		dragAbortController.abort();
		cleanupDragSelection();
	});

	function handleMouseleave(_ev: MouseEvent) {
		isHoveringSelectableArea.value = false;
	}

	return {
		selectionRect,
		isCursorSelecting,
		isHoveringSelectableArea,
		isSelecting: computed(() => selectionRect.value.isSelecting),
		handleMousedown,
		handleMousemove,
		handleMouseup,
		handleMouseleave,
		handleDocumentMouseup,
	};
}
