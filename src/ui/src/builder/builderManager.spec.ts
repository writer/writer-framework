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
	});
});
