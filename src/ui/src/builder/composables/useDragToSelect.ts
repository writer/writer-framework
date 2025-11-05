import {
	ref,
	shallowRef,
	computed,
	type Ref,
	onUnmounted,
	nextTick,
} from "vue";
import type { BuilderManager } from "@/writerTypes";
import { useAbortController } from "@/composables/useAbortController";

interface SelectionRectangle {
	isSelecting: boolean;
	startX: number;
	startY: number;
	left: number;
	top: number;
	width: number;
	height: number;
}

interface ScreenCoordinates {
	left: number;
	top: number;
	right: number;
	bottom: number;
}

const MIN_SELECTION_SIZE_PX = 5;

interface UseDragToSelectOptions {
	wrapperRef: Ref<HTMLElement | null>;
	builderManager: BuilderManager;
	isAnnotating: Ref<boolean>;
}

export function useDragToSelect(options: UseDragToSelectOptions) {
	const { wrapperRef, builderManager, isAnnotating } = options;

	const selectionRect = shallowRef<SelectionRectangle>({
		isSelecting: false,
		startX: 0,
		startY: 0,
		left: 0,
		top: 0,
		width: 0,
		height: 0,
	});

	const dragAbortController = useAbortController();

	const isCursorSelecting = computed(() => selectionRect.value.isSelecting);

	const isHoveringSelectableArea = ref(false);
	const justCompletedDragSelection = ref(false);

	let dragMousemoveAbortController: AbortController | null = null;
	let hoverUpdateRafId: number | null = null;
	let pendingHoverEvent: MouseEvent | null = null;
	let selectionUpdateRafId: number | null = null;
	let pendingSelectionEvent: MouseEvent | null = null;
	let clickBlockerTimeoutId: ReturnType<typeof setTimeout> | null = null;

	function updateHoverState(ev: MouseEvent) {
		if (builderManager.mode.value === "preview") {
			isHoveringSelectableArea.value = false;
			return;
		}
		if (isAnnotating.value) {
			isHoveringSelectableArea.value = false;
			return;
		}

		if (ev.shiftKey || ev.ctrlKey || ev.metaKey) {
			isHoveringSelectableArea.value = false;
			return;
		}

		if (builderManager.mode.value === "blueprints" && !ev.altKey) {
			isHoveringSelectableArea.value = false;
			return;
		}

		if (!(ev.target instanceof Element)) {
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
			if (builderManager.mode.value === "blueprints") {
				if (!shouldAllowSelectionInBlueprints(target)) {
					isHoveringSelectableArea.value = false;
					return;
				}
			} else {
				isHoveringSelectableArea.value = false;
				return;
			}
		}

		if (!isTargetSelectable(target)) {
			isHoveringSelectableArea.value = false;
			return;
		}

		if (builderManager.mode.value === "blueprints") {
			if (!isClickOnBlueprintsCanvas(target)) {
				isHoveringSelectableArea.value = false;
				return;
			}
		}

		isHoveringSelectableArea.value = true;
	}

	function shouldAllowDragSelection(event: MouseEvent): boolean {
		if (builderManager.mode.value === "preview" || isAnnotating.value) {
			return false;
		}

		if (builderManager.mode.value === "blueprints") {
			if (!event.altKey) return false;
			if (event.shiftKey || event.ctrlKey || event.metaKey) return false;
			return true;
		} else {
			if (
				event.shiftKey ||
				event.ctrlKey ||
				event.metaKey ||
				event.altKey
			) {
				return false;
			}
			return true;
		}
	}

	function shouldAllowSelectionInBlueprints(target: HTMLElement): boolean {
		const targetEl = target.closest<HTMLElement>("[data-writer-id]");
		if (!targetEl) return true;

		const blueprintsBlueprint = target.closest<HTMLElement>(
			".BlueprintsBlueprint",
		);
		if (!blueprintsBlueprint) return false;

		return targetEl === blueprintsBlueprint;
	}

	function isClickOnBlueprintsCanvas(target: HTMLElement): boolean {
		const blueprintsBlueprint = target.closest<HTMLElement>(
			".BlueprintsBlueprint",
		);
		if (!blueprintsBlueprint) return false;

		const nodeContainer =
			blueprintsBlueprint.querySelector<HTMLElement>(".nodeContainer");
		return nodeContainer ? nodeContainer.contains(target) : false;
	}

	function isTargetSelectable(target: HTMLElement): boolean {
		const unselectableEl = target.closest<HTMLElement>(
			"[data-writer-unselectable]",
		);
		if (unselectableEl) return false;

		if (target.classList.contains("selectionRectangle")) return false;

		return true;
	}

	function findComponentsInSelectionRect(
		wrapper: HTMLElement,
		selectionRectAbsolute: ScreenCoordinates,
	): Array<{ componentId: string; instancePath?: string }> {
		const allComponentEls =
			wrapper.querySelectorAll<HTMLElement>("[data-writer-id]");
		const selectedComponents: Array<{
			componentId: string;
			instancePath?: string;
		}> = [];

		for (const element of Array.from(allComponentEls)) {
			if (element.closest("[data-writer-unselectable]")) continue;

			const componentRect = element.getBoundingClientRect();

			const isContained =
				componentRect.left >= selectionRectAbsolute.left &&
				componentRect.right <= selectionRectAbsolute.right &&
				componentRect.top >= selectionRectAbsolute.top &&
				componentRect.bottom <= selectionRectAbsolute.bottom;

			if (isContained) {
				const componentId = element.dataset.writerId;
				const instancePath = element.dataset.writerInstancePath;
				if (componentId) {
					selectedComponents.push({
						componentId,
						instancePath:
							instancePath && instancePath.trim()
								? instancePath
								: undefined,
					});
				}
			}
		}

		return selectedComponents;
	}

	function cleanupDragSelection() {
		if (!selectionRect.value.isSelecting) return;

		if (dragMousemoveAbortController) {
			dragMousemoveAbortController.abort();
			dragMousemoveAbortController = null;
		}

		if (hoverUpdateRafId !== null) {
			cancelAnimationFrame(hoverUpdateRafId);
			hoverUpdateRafId = null;
		}
		pendingHoverEvent = null;

		if (selectionUpdateRafId !== null) {
			cancelAnimationFrame(selectionUpdateRafId);
			selectionUpdateRafId = null;
		}
		pendingSelectionEvent = null;

		if (clickBlockerTimeoutId !== null) {
			clearTimeout(clickBlockerTimeoutId);
			clickBlockerTimeoutId = null;
		}

		selectionRect.value = {
			...selectionRect.value,
			isSelecting: false,
		};
		document.body.style.userSelect = "";
		document.body.style.cursor = "";
	}

	function getTransformScale(element: HTMLElement): {
		scaleX: number;
		scaleY: number;
	} {
		const computedStyle = window.getComputedStyle(element);
		const transform = computedStyle.transform;
		let scaleX = 1;
		let scaleY = 1;

		if (transform && transform !== "none") {
			const matrix = transform.match(/matrix\(([^)]+)\)/);
			if (matrix) {
				const values = matrix[1]
					.split(",")
					.map((v) => parseFloat(v.trim()));
				if (values.length >= 4) {
					scaleX = values[0];
					scaleY = values[3];
				}
			}
		}

		return { scaleX, scaleY };
	}

	function convertSelectionRectToScreenCoordinates(
		wrapper: HTMLElement,
		selectionRect: {
			left: number;
			top: number;
			width: number;
			height: number;
		},
	): ScreenCoordinates {
		const wrapperRect = wrapper.getBoundingClientRect();
		const { scaleX, scaleY } = getTransformScale(wrapper);

		return {
			left: wrapperRect.left + selectionRect.left * scaleX,
			top: wrapperRect.top + selectionRect.top * scaleY,
			right:
				wrapperRect.left +
				(selectionRect.left + selectionRect.width) * scaleX,
			bottom:
				wrapperRect.top +
				(selectionRect.top + selectionRect.height) * scaleY,
		};
	}

	function updateSelectionRectImpl(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) return;
		if (builderManager.mode.value === "preview") return;

		const wrapper = wrapperRef.value;
		if (!wrapper) return;

		try {
			const wrapperRect = wrapper.getBoundingClientRect();
			const { scaleX, scaleY } = getTransformScale(wrapper);

			const currentX = (ev.clientX - wrapperRect.left) / scaleX;
			const currentY =
				(ev.clientY - wrapperRect.top) / scaleY + wrapper.scrollTop;

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

	function updateSelectionRect(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) return;
		if (builderManager.mode.value === "preview") return;

		pendingSelectionEvent = ev;
		if (selectionUpdateRafId === null) {
			selectionUpdateRafId = requestAnimationFrame(() => {
				if (pendingSelectionEvent) {
					updateSelectionRectImpl(pendingSelectionEvent);
					pendingSelectionEvent = null;
				}
				selectionUpdateRafId = null;
			});
		}
	}

	function handleDragSelectionMousemove(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) return;
		updateSelectionRect(ev);
		ev.preventDefault();
	}

	function handleMousedown(ev: MouseEvent) {
		if (!shouldAllowDragSelection(ev)) {
			return;
		}

		if (!(ev.target instanceof Element)) return;

		const target = ev.target as HTMLElement;

		const targetEl = target.closest<HTMLElement>("[data-writer-id]");
		if (targetEl) {
			if (builderManager.mode.value === "blueprints") {
				const allowed = shouldAllowSelectionInBlueprints(target);
				if (!allowed) return;
			} else {
				return;
			}
		}

		if (!isTargetSelectable(target)) {
			return;
		}

		const wrapper = wrapperRef.value;
		if (!wrapper) {
			return;
		}

		if (!wrapper.contains(target)) {
			return;
		}

		ev.stopPropagation();
		ev.preventDefault();

		const wrapperRect = wrapper.getBoundingClientRect();
		const { scaleX, scaleY } = getTransformScale(wrapper);

		const startX = (ev.clientX - wrapperRect.left) / scaleX;
		const startY =
			(ev.clientY - wrapperRect.top) / scaleY + wrapper.scrollTop;

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

		dragMousemoveAbortController = new AbortController();
		wrapper.addEventListener("mousemove", handleDragSelectionMousemove, {
			signal: dragMousemoveAbortController.signal,
		});
	}

	function handleMousemove(ev: MouseEvent) {
		if (selectionRect.value.isSelecting) {
			if (builderManager.mode.value === "blueprints") {
				ev.stopPropagation();
			}
			updateSelectionRect(ev);
			ev.preventDefault();
			return;
		}

		pendingHoverEvent = ev;
		if (hoverUpdateRafId === null) {
			hoverUpdateRafId = requestAnimationFrame(() => {
				if (pendingHoverEvent) {
					updateHoverState(pendingHoverEvent);
					pendingHoverEvent = null;
				}
				hoverUpdateRafId = null;
			});
		}
	}

	function handleMouseup(ev: MouseEvent) {
		if (!selectionRect.value.isSelecting) {
			return;
		}
		if (builderManager.mode.value === "preview") {
			cleanupDragSelection();
			return;
		}

		const { left, top, width, height } = selectionRect.value;

		if (width < MIN_SELECTION_SIZE_PX || height < MIN_SELECTION_SIZE_PX) {
			cleanupDragSelection();
			return;
		}

		ev.stopPropagation();
		ev.preventDefault();
		ev.stopImmediatePropagation();

		const wrapper = wrapperRef.value;
		if (!wrapper) {
			cleanupDragSelection();
			return;
		}

		const selectionRectAbsolute = convertSelectionRectToScreenCoordinates(
			wrapper,
			{ left, top, width, height },
		);

		const selectedComponents = findComponentsInSelectionRect(
			wrapper,
			selectionRectAbsolute,
		);

		if (selectedComponents.length > 0) {
			const [first, ...rest] = selectedComponents;
			builderManager.setSelection(
				first.componentId,
				first.instancePath,
				"click",
			);
			rest.forEach(({ componentId, instancePath }) => {
				builderManager.appendSelection(
					componentId,
					instancePath,
					"click",
				);
			});
			justCompletedDragSelection.value = true;
			if (clickBlockerTimeoutId) {
				clearTimeout(clickBlockerTimeoutId);
			}
			nextTick().then(() => {
				requestAnimationFrame(() => {
					justCompletedDragSelection.value = false;
					clickBlockerTimeoutId = null;
				});
			});
		} else {
			builderManager.setSelection(null);
		}

		cleanupDragSelection();
	}

	function handleDocumentMouseup(ev: MouseEvent) {
		if (selectionRect.value.isSelecting) {
			const wrapper = wrapperRef.value;
			if (
				wrapper &&
				ev.target instanceof Node &&
				wrapper.contains(ev.target)
			) {
				return;
			}
			cleanupDragSelection();
		}
	}

	function handleDocumentClick(ev: MouseEvent) {
		if (justCompletedDragSelection.value) {
			ev.preventDefault();
			ev.stopPropagation();
			ev.stopImmediatePropagation();
		}
	}

	onUnmounted(() => {
		if (clickBlockerTimeoutId) {
			clearTimeout(clickBlockerTimeoutId);
		}
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
		justCompletedDragSelection,
		handleMousedown,
		handleMousemove,
		handleMouseup,
		handleMouseleave,
		handleDocumentMouseup,
		handleDocumentClick,
	};
}
