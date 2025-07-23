import { describe, it, expect } from "vitest";
import { useHistoryStack } from "./useHistoryStack";

describe(useHistoryStack.name, () => {
	it("should undo", () => {
		const history = useHistoryStack();
		history.push(1);
		history.push(2);
		history.push(3);
		expect(history.undo()).toBe(2);
		expect(history.undo()).toBe(1);
	});

	it("should redo", () => {
		const history = useHistoryStack();
		history.push(1);
		history.push(2);
		history.push(3);
		expect(history.undo()).toBe(2);
		expect(history.undo()).toBe(1);
		expect(history.redo()).toBe(2);
	});

	it("should mix undo / push", () => {
		const history = useHistoryStack();
		history.push(1);
		history.push(2);
		history.push(3);
		expect(history.undo()).toBe(2);
		history.push(4);
		expect(history.undo()).toBe(2);
	});

	it("should handle undo on empty stack", () => {
		const history = useHistoryStack();
		expect(history.undo()).toBeUndefined();
	});

	it("should not undo beyond first item", () => {
		const history = useHistoryStack();
		history.push(1);
		history.push(2);
		expect(history.undo()).toBe(1);
		expect(history.undo()).toBeUndefined(); // Should not go below first item
	});

	it("should not redo beyond last item", () => {
		const history = useHistoryStack();
		history.push(1);
		history.push(2);
		expect(history.redo()).toBeUndefined(); // Already at the end
	});

	it("should handle complex undo/redo sequences", () => {
		const history = useHistoryStack();
		history.push(1);
		history.push(2);
		history.push(3);
		expect(history.undo()).toBe(2);
		expect(history.undo()).toBe(1);
		expect(history.redo()).toBe(2);
		expect(history.redo()).toBe(3);
		expect(history.redo()).toBeUndefined(); // Can't redo further
	});
});
