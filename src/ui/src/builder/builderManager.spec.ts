import { describe, it, expect } from "vitest";
import { generateBuilderManager, SelectionStatus } from "./builderManager";

describe(generateBuilderManager.name, () => {
	describe("selection", () => {
		it("should select an element", () => {
			const {
				setSelection,
				isComponentIdSelected,
				selectionStatus,
				firstSelectedId,
			} = generateBuilderManager();

			setSelection("componentId", "instancePath", "click");

			expect(firstSelectedId.value).toBe("componentId");
			expect(isComponentIdSelected("componentId")).toBeTruthy();
			expect(selectionStatus.value).toBe(SelectionStatus.Single);
		});

		it("should select multiple element", () => {
			const {
				setSelection,
				appendSelection,
				isComponentIdSelected,
				selectionStatus,
				firstSelectedId,
			} = generateBuilderManager();

			setSelection("componentId", "instancePath", "click");
			appendSelection("componentId2", "instancePath2", "click");

			expect(firstSelectedId.value).toBe("componentId");
			expect(isComponentIdSelected("componentId")).toBeTruthy();
			expect(isComponentIdSelected("componentId2")).toBeTruthy();
			expect(selectionStatus.value).toBe(SelectionStatus.Multiple);
		});

		it("should clear the selection an element", () => {
			const {
				setSelection,
				isComponentIdSelected,
				selectionStatus,
				firstSelectedId,
			} = generateBuilderManager();

			setSelection("componentId", "instancePath", "click");
			setSelection(null);

			expect(firstSelectedId.value).toBeUndefined();
			expect(isComponentIdSelected("componentId")).toBeFalsy();
			expect(selectionStatus.value).toBe(SelectionStatus.None);
		});

		it("should handle click events", () => {
			const {
				handleSelectionFromEvent,
				isComponentIdSelected,
				selectionStatus,
			} = generateBuilderManager();

			handleSelectionFromEvent({ ctrlKey: true } as KeyboardEvent, "1");

			expect(selectionStatus.value).toBe(SelectionStatus.Single);
			expect(isComponentIdSelected("1")).toBeTruthy();

			handleSelectionFromEvent({ ctrlKey: true } as KeyboardEvent, "2");

			expect(selectionStatus.value).toBe(SelectionStatus.Multiple);
			expect(isComponentIdSelected("1")).toBeTruthy();
			expect(isComponentIdSelected("2")).toBeTruthy();

			handleSelectionFromEvent({ ctrlKey: true } as KeyboardEvent, "2");

			expect(selectionStatus.value).toBe(SelectionStatus.Single);
			expect(isComponentIdSelected("1")).toBeTruthy();
			expect(isComponentIdSelected("2")).toBeFalsy();
		});
	});
});
