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
function doRangeOverlap(a1: number, a2: number, b1: number, b2: number) {
	return (
		isInRange(a1, b1, b2) ||
		isInRange(a2, b1, b2) ||
		isInRange(b1, a1, a2) ||
		isInRange(b2, a1, a2)
	);
}

export function doRectanglesOverlap(a: Rectangle, b: Rectangle): boolean {
	const isXOverlaping = doRangeOverlap(
		a.x,
		a.x + a.width,
		b.x,
		b.x + b.width,
	);
	const isYOverlaping = doRangeOverlap(
		a.y,
		a.y + a.height,
		b.y,
		b.y + b.height,
	);

	return isXOverlaping && isYOverlaping;
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
		return !otherRectangles.some((r) => doRectanglesOverlap(rect, r));
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
