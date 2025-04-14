import { describe, expect, it } from "vitest";
import {
	Rectangle,
	doRectanglesOverlap,
	computePointInTheGrid,
	positionateRectangleWithoutColision,
} from "./geometry";

describe(doRectanglesOverlap.name, () => {
	const initialRect: Rectangle = { x: 10, y: 10, width: 10, height: 10 };

	it.each([
		{ x: 0, y: 0, width: 10, height: 10 },
		{ x: 19, y: 19, width: 10, height: 10 },
		{ x: 12, y: 12, width: 2, height: 2 },
		{ x: 0, y: 0, width: 30, height: 30 },
		{ x: 15, y: 15, width: 10, height: 15 },
	])("should overlap for %s", (rect) => {
		expect(doRectanglesOverlap(initialRect, rect)).toBe(true);
	});
	it("should overlap for", () => {
		expect(
			doRectanglesOverlap(
				{ width: 240, height: 124, x: 48, y: 120 },
				{ width: 240, height: 167, x: 72, y: 96 },
			),
		).toBe(true);
	});

	it.each([
		{ x: 0, y: 0, width: 1, height: 1 },
		{ x: 30, y: 30, width: 10, height: 10 },
	])("should not overlap for %s", (rect) => {
		expect(doRectanglesOverlap(initialRect, rect)).toBe(false);
	});
});

describe(computePointInTheGrid.name, () => {
	it("should round the axis", () => {
		expect(computePointInTheGrid({ x: 0.6, y: 1.4 }, 1)).toStrictEqual({
			x: 0,
			y: 1,
		});
	});

	it("should not round the axis", () => {
		expect(computePointInTheGrid({ x: 0, y: 1 }, 1)).toStrictEqual({
			x: 0,
			y: 1,
		});
	});
});

describe(positionateRectangleWithoutColision.name, () => {
	const rectangles: Rectangle[] = [{ x: 10, y: 10, width: 10, height: 10 }];

	it.each([
		{
			input: { x: 20, y: 20, width: 10, height: 10 },
			expected: { x: 20, y: 21, width: 10, height: 10 },
		},
		{
			input: { x: 9, y: 9, width: 10, height: 10 },
			expected: { x: 9, y: 21, width: 10, height: 10 },
		},
		{
			input: { x: 1, y: 1, width: 10, height: 10 },
			expected: { x: 1, y: 21, width: 10, height: 10 },
		},
		{
			input: { x: 0, y: 10, width: 10, height: 10 },
			expected: { x: 0, y: 21, width: 10, height: 10 },
		},
	])("should positionate the rectange $input", ({ input, expected }) => {
		expect(
			positionateRectangleWithoutColision(input, rectangles, 1),
		).toStrictEqual(expected);
	});
});
