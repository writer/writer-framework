export function isPlainObject(
	input: unknown,
): input is Record<string, unknown> {
	return typeof input === "object" && input !== null && !Array.isArray(input);
}

export function* extractObjectPaths(
	obj: unknown,
	prefix = "",
	visited = new WeakSet(),
): Generator<string> {
	if (!isPlainObject(obj)) return;
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

export function isPlainObjectDeepEqual(a: unknown, b: unknown): boolean {
	if (a === b) return true;

	if (a === null || b === null || !isPlainObject(a) || !isPlainObject(b)) {
		return false;
	}

	const keysA = Object.keys(a);
	const keysB = Object.keys(b);

	// Different number of keys
	if (keysA.length !== keysB.length) {
		return false;
	}

	// Compare each key and value
	for (const key of keysA) {
		if (!keysB.includes(key)) {
			return false;
		}
		if (!isPlainObjectDeepEqual(a[key], b[key])) {
			return false;
		}
	}

	return true;
}
