export type Point = { x: number; y: number };

export function computeDistance(a: Point, b: Point) {
	return Math.hypot(b.x - a.x, b.y - a.y);
}
export function computePointInTheGrid(
	{ x, y }: Point,
	gridTick: number,
): Point {
	return {
		x: x - (x % gridTick),
		y: y - (y % gridTick),
	};
}

export function translatePoint({ x, y }: Point, { x: tx, y: ty }: Point) {
	return { x: x + tx, y: y + ty };
}

export type Rectangle = Point & { width: number; height: number };

function getRectangeCenterPoint(rect: Rectangle): Point {
	return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
}

function isInRange(value: number, min: number, max: number) {
	return value >= min && value <= max;
}

export function areRectanglesColliding(a: Rectangle, b: Rectangle): boolean {
	return (
		isInRange(a.x, b.x, b.x + b.width) ||
		isInRange(b.x, a.x, a.x + a.width) ||
		isInRange(a.y, b.y, b.y + b.height) ||
		isInRange(b.y, a.y, a.y + a.height)
	);

	if (isInRange(a.x, b.x, b.x + b.width)) return true;
	if (isInRange(b.x, a.x, a.x + a.width)) return true;
	if (isInRange(a.y, b.y, b.y + b.height)) return true;
	if (isInRange(b.y, a.y, a.y + a.height)) return true;
	return false;
	// if (isInRange(b.x, a.x, a.x + a.width)) return true;
	return !(
		a.x + a.width <= b.x ||
		a.x >= b.x + b.width ||
		a.y + a.height <= b.y ||
		a.y >= b.y + b.height
	);
}

/**
 *
 */
export function positionateRectangleWithoutColision(
	target: Rectangle,
	otherRectangles: Rectangle[],
	gridTick: number,
): Rectangle {
	const directions: Point[] = [
		{ x: -gridTick, y: -gridTick },
		{ x: -gridTick, y: 0 },
		{ x: -gridTick, y: gridTick },
		{ x: 0, y: -gridTick },
		{ x: 0, y: gridTick },
		{ x: gridTick, y: -gridTick },
		{ x: gridTick, y: 0 },
		{ x: gridTick, y: gridTick },
	];
	const visited = new Set();
	const queue: Point[] = [];
	const solutions: Point[] = [];

	function buildRectangleFromPoint({ x, y }: Point): Rectangle {
		return { width: target.width, height: target.height, x, y };
	}

	function isPointValid(point: Point) {
		if (point.x < 0 || point.y < 0) return false;
		const rect = buildRectangleFromPoint(point);
		return !otherRectangles.some((r) => areRectanglesColliding(rect, r));
	}

	function addQueue(p: Point) {
		const key = `${p.x},${p.y}`;
		if (visited.has(key)) return;
		queue.push(p);
		visited.add(key);
	}

	addQueue({ x: target.x, y: target.y });

	while (queue.length) {
		const point = queue.shift();
		if (point === undefined) return undefined;

		if (isPointValid(point)) {
			solutions.push(point);
		}

		if (solutions.length === 0) {
			for (const direction of directions) {
				addQueue(translatePoint(point, direction));
			}
		}
	}

	const targetCenter = getRectangeCenterPoint(target);

	const getDistanceFromTarget = (p: Point) =>
		computeDistance(
			targetCenter,
			getRectangeCenterPoint(buildRectangleFromPoint(p)),
		);

	const point = solutions
		.sort((a, b) => getDistanceFromTarget(a) - getDistanceFromTarget(b))
		.shift();
	if (point) return buildRectangleFromPoint(point);

	return;
}
