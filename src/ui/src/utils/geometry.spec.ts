import { describe, expect, it } from "vitest";
import {
	Rectangle,
	areRectanglesColliding,
	computePointInTheGrid,
	positionateRectangleWithoutColision,
} from "./geometry";

describe(areRectanglesColliding.name, () => {
	it("should overlap on y and y", () => {
		expect(
			areRectanglesColliding(
				{ x: 0, y: 0, width: 10, height: 10 },
				{ x: 9, y: 9, width: 10, height: 10 },
			),
		).toBe(true);
	});
	it("should overlap on x", () => {
		expect(
			areRectanglesColliding(
				{ x: 7, y: 10, width: 10, height: 10 },
				{ x: 0, y: 0, width: 10, height: 10 },
			),
		).toBe(true);
	});
	it("should overlap with width", () => {
		expect(
			areRectanglesColliding(
				{ x: 10, y: 10, width: 10, height: 10 },
				{ x: 5, y: 5, width: 10, height: 10 },
			),
		).toBe(true);
	});
	it("should overlap when contains the other", () => {
		expect(
			areRectanglesColliding(
				{ x: 10, y: 10, width: 10, height: 10 },
				{ x: 0, y: 0, width: 30, height: 30 },
			),
		).toBe(true);
	});
	it("should not overlap", () => {
		expect(
			areRectanglesColliding(
				{ x: 0, y: 0, width: 10, height: 10 },
				{ x: 20, y: 20, width: 10, height: 10 },
			),
		).toBe(false);
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
	const rectangles: Rectangle[] = [{ x: 0, y: 0, width: 10, height: 10 }];

	it.each([
		{
			input: { x: 20, y: 20, width: 10, height: 10 },
			expected: { x: 20, y: 20, width: 10, height: 10 },
		},
		{
			input: { x: 9, y: 9, width: 10, height: 10 },
			expected: { x: 11, y: 11, width: 10, height: 10 },
		},
		{
			input: { x: 1, y: 1, width: 10, height: 10 },
			expected: { x: 11, y: 11, width: 10, height: 10 },
		},
		{
			input: { x: 0, y: 10, width: 10, height: 10 },
			expected: { x: 11, y: 11, width: 10, height: 10 },
		},
	])("should positionate the rectange", ({ input, expected }) => {
		expect(
			positionateRectangleWithoutColision(input, rectangles, 1),
		).toStrictEqual(expected);
	});
});
