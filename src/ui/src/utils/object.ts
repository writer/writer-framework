export function* extractObjectPaths(
	obj: unknown,
	prefix = "",
	visited = new WeakSet(),
): Generator<string> {
	if (typeof obj !== "object" || obj === null) return;
	if (visited.has(obj)) return;
	visited.add(obj);

	for (const key in obj) {
		const path = prefix ? `${prefix}.${key}` : key;
		yield path;

		if (
			typeof obj[key] === "object" &&
			obj[key] !== null &&
			!Array.isArray(obj[key])
		) {
			yield* extractObjectPaths(obj[key], path, visited);
		}
	}
}
