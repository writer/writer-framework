export type Point = { x: number; y: number };

export function computeDistance(a: Point, b: Point) {
	return Math.hypot(b.x - a.x, b.y - a.y);
}
export function computePointInTheGrid(
	{ x, y }: Point,
	gridTick: number,
): Point {
	const halfTick = gridTick / 2;
	return {
		x: x - (x % gridTick) + halfTick,
		y: y - (y % gridTick) + halfTick,
	};
}

export type Rectangle = Point & { width: number; height: number };

export function areRectangesColliding(a: Rectangle, b: Rectangle): boolean {
	return !(
		a.x + a.width <= b.x ||
		a.x >= b.x + b.width ||
		a.y + a.height <= b.y ||
		a.y >= b.y + b.height
	);
}

export function positionateRectangleWithoutColision(
	target: Rectangle,
	otherRectangles: Rectangle[],
): Point {
	const collidingRect = otherRectangles.find((rect) =>
		areRectangesColliding(target, rect),
	);

	if (!collidingRect) return target;

	const newPosition: Rectangle = { ...target };

	const left = collidingRect.x - newPosition.x;
	const right = newPosition.x - (collidingRect.x + collidingRect.width);
	const top = collidingRect.y - newPosition.y;
	const bottom = newPosition.y - (collidingRect.y + collidingRect.height);

	const minDistance = Math.min(left, right, top, bottom);

	if (minDistance === left) {
		newPosition.x = collidingRect.x - newPosition.width;
	} else if (minDistance === right) {
		newPosition.x = collidingRect.x + collidingRect.width;
	} else if (minDistance === top) {
		newPosition.y = collidingRect.y - newPosition.height;
	} else if (minDistance === bottom) {
		newPosition.y = collidingRect.y + collidingRect.height;
	}

	return positionateRectangleWithoutColision(newPosition, otherRectangles);
}
