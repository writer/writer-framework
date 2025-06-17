const UNSAFE_OBJECT_KEYS = new Set([
	"__proto__",
	"constructor",
	"prototype",
	"hasOwnProperty",
	"isPrototypeOf",
	"propertyIsEnumerable",
	"__defineGetter__",
	"__defineSetter__",
	"__lookupGetter__",
	"__lookupSetter__",
]);

/**
 * Sets a nested property on an object based on a dot-separated path.
 *
 * This function mutates the original object in-place. If any part of the path does not exist, it will be created as a plain object.
 *
 * @param obj The object to modify.
 * @param path The dot-separated path indicating where to set the value (e.g., "user.profile.name").
 * @param value The value to assign at the specified path.
 *
 * @example
 * const data = {};
 * setValueAtPath(data, 'config.theme.color', 'blue');
 * console.log(data); // { config: { theme: { color: 'blue' } } }
 */
export function setValueAtPath(
	obj: Record<string, unknown>,
	path: string,
	value: unknown,
): void {
	if (!path) return; // gracefully ignore empty paths

	const keys = path.split(".").filter(Boolean);
	let current: Record<string, unknown> = obj;

	for (let i = 0; i < keys.length; i++) {
		const key = keys[i];

		// Block unsafe keys to prevent prototype pollution
		if (UNSAFE_OBJECT_KEYS.has(key)) {
			throw new Error(`Unsafe key detected: ${key}`);
		}

		const isLast = i === keys.length - 1;
		const next = current[key];

		if (isLast) {
			current[key] = value;
		} else {
			// Replace if missing, null, not an object, or an array
			if (
				typeof next !== "object" ||
				next === null ||
				Array.isArray(next)
			) {
				current[key] = {};
			}

			current = current[key] as Record<string, unknown>;
		}
	}
}

/**
 * Retrieves a nested value from an object based on a dot-separated path.
 *
 * If the path does not exist, `undefined` is returned.
 *
 * @param path - The dot-separated path to access (e.g., "user.profile.name").
 * @param obj - The object to retrieve the value from.
 * @returns The value at the specified path, or `undefined` if not found.
 *
 * @example
 * const user = { profile: { name: 'Alice' } };
 * const name = getValueAtPath('profile.name', user); // 'Alice'
 */
export function getValueAtPath(
	obj: Record<string, unknown>,
	path: string,
): unknown {
	if (!path) return undefined;

	const keys = path.split(".");
	let current: unknown = obj;

	for (const key of keys) {
		if (
			typeof current !== "object" ||
			current === null ||
			!(key in current)
		) {
			return undefined;
		}
		current = (current as Record<string, unknown>)[key];
	}

	return current;
}

/**
 * Deeply merges two objects and returns the result.
 *
 * This function does not mutate the inputs. Nested objects are merged recursively.
 * Arrays and primitives in the source override those in the target by default.
 *
 * @param target - The base object.
 * @param source - The object to merge into the base.
 * @returns A new object with merged values.
 *
 * @example
 * const a = { user: { name: 'Alice', roles: ['admin'] } };
 * const b = { user: { age: 30, roles: ['editor'] } };
 * const result = deepMerge(a, b);
 * // result: { user: { name: 'Alice', age: 30, roles: ['editor'] } }
 */
export function deepMerge<T extends object, U extends object>(
	target: T,
	source: U,
): T & U {
	const result: unknown = { ...target };

	for (const key in source) {
		if (!Object.prototype.hasOwnProperty.call(source, key)) continue;
		if (UNSAFE_OBJECT_KEYS.has(key)) {
			throw new Error(`Unsafe key detected: ${key}`);
		}

		const targetValue = (target as unknown)[key];
		const sourceValue = (source as unknown)[key];

		if (isObject(targetValue) && isObject(sourceValue)) {
			result[key] = deepMerge(targetValue, sourceValue);
		} else {
			result[key] = sourceValue;
		}
	}

	return result as T & U;
}

export function isObject(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}
