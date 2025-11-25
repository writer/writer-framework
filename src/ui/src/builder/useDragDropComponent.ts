import { Ref, ref } from "vue";
import { Core, Component } from "@/writerTypes";
import { CANDIDATE_CONFIRMATION_DELAY_MS } from "./builderManager";

/*
In Renderer, the drag and drop of components goes through two phases:

1. Unconfirmed candidate phase. 
Insertion overlay is updated as the user hovers over different component and
viable parents. These potential parents are "candidates".
After CANDIDATE_CONFIRMATION_DELAY_MS milliseconds, the active potential 
parent becomes a confirmed candidate.
If the drop happens before the candidate is confirmed, no position is provided.

2. Confirmed candidate phase.
When a candidate is confirmed, the user loses the ability to switch to another candidate.
The confirmed candidate's container is "cracked open" and its insertion slots are revealed.
The insertion slots will allow the user to choose an exact position in which
to insert the dragged component.
If the user gets off bounds by MAX_DISTANCE_FROM_CANDIDATE_PX, the candidacy is rejected.

*/

const MAX_DISTANCE_FROM_CANDIDATE_PX = 30;
const dragDropMimeRegex =
	/^application\/json;writer=(?<componentType>\w+),(?<componentId>[\w\-]*)$/;
const candidateId: Ref<Component["id"]> = ref(null);
const candidateInstancePath: Ref<string> = ref(null);
const isCandidacyConfirmed: Ref<boolean> = ref(false);
let candidacyStartTime: number = null;
let insertionPosition: number = null;

// Regex to extract source blueprint ID from shared blueprint MIME type
// Format: application/json;writer=shared_blueprint,SOURCE_BLUEPRINT_ID
const sharedBlueprintMimeRegex =
	/^application\/json;writer=shared_blueprint,(?<sourceBlueprintId>[\w\-]*)$/;

export function useDragDropComponent(wf: Core) {
	function getComponentInfoFromDrag(ev: DragEvent) {
		const allTypes = Array.from(ev.dataTransfer.types);
		
		// Check all MIME types for shared blueprint first (special handling)
		for (const mimeType of allTypes) {
			if (mimeType?.startsWith("application/json;writer=shared_blueprint")) {
				// Extract the source blueprint ID from the MIME type
				const match = mimeType.match(sharedBlueprintMimeRegex);
				const sourceBlueprintId = match?.groups?.sourceBlueprintId || "";
				return {
					draggedType: "shared_blueprint",
					draggedId: "",
					sourceBlueprintId, // Pass the ID extracted from MIME type
				};
			}
		}
		
		// Then check the first MIME type with the regex
		const mimeString: string = allTypes[0];
		const matchGroups = mimeString?.match(dragDropMimeRegex)?.groups;
		if (!matchGroups) {
			return;
		}
		const result = {
			draggedType: matchGroups.componentType,
			draggedId: matchGroups.componentId,
		};
		return result;
	}

	function getIdFromElement(el: HTMLElement) {
		// Elements inside a cage aren't taken into account for insertion

		const cageEl = el.closest("[data-writer-cage]");
		const startEl = cageEl ?? el;
		const targetEl: HTMLElement = startEl.closest("[data-writer-id]");
		if (!targetEl) return;
		return targetEl.dataset.writerId;
	}

	function dropComponent(ev: DragEvent) {
		const dragInfo = getComponentInfoFromDrag(ev);
		if (!dragInfo) {
			return;
		}
		const { draggedType, draggedId } = dragInfo;
		
		// Read the JSON payload from drag data FIRST (before checking parentId)
		// This is important because getData() can only be called during the drop event
		let dragContent: Record<string, unknown> = {};
		
		// For shared blueprints, try reading from multiple sources
		if (draggedType === "shared_blueprint") {
			// Get the sourceBlueprintId from the MIME type (extracted in getComponentInfoFromDrag)
			const sourceBlueprintIdFromMime = (dragInfo as { sourceBlueprintId?: string }).sourceBlueprintId;
			
			// Try text/plain first (more reliable across browsers)
			try {
				const textData = ev.dataTransfer.getData("text/plain");
				if (textData && textData.trim() && textData !== "{}") {
					const parsed = JSON.parse(textData);
					if (Object.keys(parsed).length > 0 && parsed.sourceBlueprintId) {
						dragContent = parsed;
					}
				}
			} catch {
				// Ignore JSON parse errors
			}
			
			// Fallback: Try the custom MIME type with the ID
			if (Object.keys(dragContent).length === 0 && sourceBlueprintIdFromMime) {
				const expectedMimeType = `application/json;writer=shared_blueprint,${sourceBlueprintIdFromMime}`;
				try {
					const jsonData = ev.dataTransfer.getData(expectedMimeType);
					if (jsonData && jsonData.trim() && jsonData !== "{}") {
						const parsed = JSON.parse(jsonData);
						if (Object.keys(parsed).length > 0) {
							dragContent = parsed;
						}
					}
				} catch {
					// Ignore JSON parse errors
				}
			}
			
			// Final fallback: Use the sourceBlueprintId from the MIME type itself
			if (Object.keys(dragContent).length === 0 && sourceBlueprintIdFromMime) {
				dragContent = { sourceBlueprintId: sourceBlueprintIdFromMime };
			}
		}
		
		const dropTargetId = getIdFromElement(ev.target as HTMLElement);
		const parentId = findSuitableParent(
			dropTargetId,
			draggedId,
			draggedType,
		);
		if (!parentId) {
			return;
		}
		
		// Fallback: Try all available MIME types to find the one with JSON data
		if (Object.keys(dragContent).length === 0) {
			for (const mimeType of ev.dataTransfer.types) {
				if (mimeType.startsWith("application/json;writer=")) {
					try {
						const jsonData = ev.dataTransfer.getData(mimeType);
						if (jsonData) {
							const parsed = JSON.parse(jsonData);
							// Only use non-empty objects (empty object "{}" means no content)
							if (Object.keys(parsed).length > 0) {
								dragContent = parsed;
								break; // Use the first valid JSON data we find
							}
						}
					} catch {
						// Ignore JSON parse errors, try next MIME type
					}
				}
			}
		}

		const dropData = {
			draggedType,
			draggedId: draggedId,
			parentId: candidateId.value,
			position: insertionPosition,
			dragContent,
		};
		removeInsertionCandidacy(ev);
		return dropData;
	}

	function isParentSuitable(
		targetId: Component["id"],
		draggedId: Component["id"],
		draggedType: Component["type"],
	): boolean {
		const targetComponent = wf.getComponentById(targetId);
		if (!targetComponent) return false;
		const containableTypes = wf.getContainableTypes(targetId);
		return (
			!targetComponent?.isCodeManaged &&
			!wf.isChildOf(draggedId, targetId) &&
			containableTypes.includes(draggedType)
		);
	}

	function findSuitableParent(
		targetId: Component["id"],
		draggedId: Component["id"],
		draggedType: Component["type"],
	): Component["id"] {
		const targetComponent = wf.getComponentById(targetId);
		if (!targetComponent) return;
		if (isParentSuitable(targetId, draggedId, draggedType)) {
			return targetId;
		}

		if (!targetComponent.parentId) return null;
		return findSuitableParent(
			targetComponent.parentId,
			draggedId,
			draggedType,
		);
	}

	function assignInsertionCandidacy(ev: DragEvent) {
		if (isCandidacyConfirmed.value) {
			handleConfirmedCandidacy(ev);
			return;
		}

		handleUnconfirmedCandidacy(ev);
	}

	function handleUnconfirmedCandidacy(ev: DragEvent) {
		const dragInfo = getComponentInfoFromDrag(ev);
		if (!dragInfo) return;
		const { draggedType, draggedId } = dragInfo;
		const targetEl = ev.target as HTMLElement;
		const dropTargetId = getIdFromElement(targetEl);
		const parentId = findSuitableParent(
			dropTargetId,
			draggedId,
			draggedType,
		);
		if (!parentId || parentId == draggedId) return;
		const parentComponentEl: HTMLElement = targetEl.closest(
			`[data-writer-id="${parentId}"]`,
		);
		const parentComponentInstancePath =
			parentComponentEl.dataset.writerInstancePath;
		ev.preventDefault();

		if (candidateInstancePath.value !== parentComponentInstancePath) {
			candidacyStartTime = Date.now();
		} else if (
			Date.now() - candidacyStartTime >=
			CANDIDATE_CONFIRMATION_DELAY_MS
		) {
			isCandidacyConfirmed.value = true;
			crackContainerOpen(candidateInstancePath.value);
			return;
		}

		candidateId.value = parentId;
		candidateInstancePath.value = parentComponentInstancePath;
	}

	function handleConfirmedCandidacy(ev: DragEvent) {
		const dragInfo = getComponentInfoFromDrag(ev);
		if (!dragInfo) return;

		ev.preventDefault();

		// If the user goes too far off the candidate, reject candidacy

		const candidateEl: HTMLElement = document.querySelector(
			`[data-writer-instance-path="${candidateInstancePath.value}"]`,
		);
		if (
			getDistanceFromElement(ev.clientX, ev.clientY, candidateEl) >
			MAX_DISTANCE_FROM_CANDIDATE_PX
		) {
			removeInsertionCandidacy(ev);
			return;
		}

		// Find nearest slot and its position

		const slotEls = getSlotElementsOfCrackedContainer(
			candidateInstancePath.value,
		);
		if (slotEls.length == 0) return;

		const nearestSlot = getNearestSlot(ev.clientX, ev.clientY, slotEls);
		if (!nearestSlot) {
			return;
		}
		const { el: nearestSlotEl } = nearestSlot;

		const { draggedId } = dragInfo;
		const slotPosition = parseInt(nearestSlotEl.dataset.writerPosition);
		const draggedComponent = wf.getComponentById(draggedId);

		slotEls.map((el) => {
			if (!el.classList.contains("highlighted")) return;
			el.classList.remove("highlighted");
		});
		if (nearestSlotEl.classList.contains("highlighted")) return;
		nearestSlotEl.classList.add("highlighted");

		if (
			draggedComponent &&
			draggedComponent.parentId == candidateId.value &&
			slotPosition > draggedComponent.position
		) {
			// Account for the component staying in the same container.

			insertionPosition = slotPosition - 1;
			return;
		}

		insertionPosition = slotPosition;
	}

	function getSlotElementsOfCrackedContainer(instancePath: string) {
		const el = getContainerInInstancePath(instancePath);
		const slotEls: HTMLElement[] = Array.from(
			el.querySelectorAll(`[data-writer-position]`),
		);
		return slotEls;
	}

	function getNearestSlot(x: number, y: number, slotEls: HTMLElement[]) {
		// Calculate distance from nearest vertex and sort

		const slotsElsWithDistance = slotEls
			.map((el: HTMLElement) => {
				return { el, distance: getDistanceFromElement(x, y, el) };
			})
			.sort((a, b): number => (a.distance > b.distance ? 1 : -1));

		return slotsElsWithDistance?.[0];
	}

	function getDistanceFromElement(x: number, y: number, el: HTMLElement) {
		const { top, left, right, bottom } = el.getBoundingClientRect();
		const dx = Math.max(left - x, 0, x - right);
		const dy = Math.max(top - y, 0, y - bottom);
		const distance = Math.sqrt(dx * dx + dy * dy);
		return distance;
	}

	/**
	 * Cracks a container open, revealing its insertion slots.
	 */
	function crackContainerOpen(instancePath: string) {
		const el = getContainerInInstancePath(instancePath);
		el.classList.add("crackedContainer");
	}

	function restoreCrackedContainer(instancePath: string) {
		const el = getContainerInInstancePath(instancePath);
		el.classList.remove("crackedContainer");
	}

	function getContainerInInstancePath(instancePath: string): HTMLElement {
		const rootEl: HTMLElement = document.querySelector(
			`[data-writer-instance-path="${instancePath}"]`,
		);
		if (rootEl.hasAttribute("data-writer-container")) {
			return rootEl;
		}
		const containers = rootEl.querySelectorAll(
			`[data-writer-container]`,
		);
		for (let i = 0; i < containers.length; i++) {
			const container = containers[i];

			// If the closest root element is the root element previously identified,
			// the container belongs to the component in question -not to a child.

			const closestRootEl = container.closest(
				"[data-writer-instance-path]",
			);
			if (closestRootEl == rootEl) {
				return container as HTMLElement;
			}
		}
		return;
	}

	function removeInsertionCandidacy(ev: Event): void {
		ev.preventDefault();
		if (candidateInstancePath.value) {
			restoreCrackedContainer(candidateInstancePath.value);
			candidateInstancePath.value = null;
		}
		candidateId.value = null;
		candidacyStartTime = null;
		insertionPosition = null;
		isCandidacyConfirmed.value = false;
	}

	return {
		candidateId,
		candidateInstancePath,
		isParentSuitable,
		isCandidacyConfirmed,
		getComponentInfoFromDrag,
		dropComponent,
		assignInsertionCandidacy,
		removeInsertionCandidacy,
	};
}
