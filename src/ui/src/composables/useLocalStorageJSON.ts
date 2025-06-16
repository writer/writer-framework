import { computed, shallowRef } from "vue";

/**
 * Get/Set the JSON object in localStorage
 * @param validator Validate that the data has a given shape; remove the localStorage value if the validator returns `false`.
 */
export function useLocalStorageJSON<T>(
	key: string,
	validator?: (value: T) => boolean,
) {
	const actualValue = shallowRef<T | undefined>(get());

	function hasLocalStorage() {
		return (
			typeof window !== "undefined" &&
			typeof window.localStorage !== "undefined"
		);
	}

	function get() {
		if (!hasLocalStorage()) return undefined;

		const value = localStorage.getItem(key);
		if (!value) return undefined;

		try {
			const data = JSON.parse(value);
			if (validator?.(data) === false) {
				localStorage.removeItem(key);
				return undefined;
			}
			return data;
		} catch {
			localStorage.removeItem(key);
			return undefined;
		}
	}

	return computed<T | undefined>({
		get() {
			return actualValue.value;
		},
		set(value) {
			actualValue.value = value;
			if (!hasLocalStorage()) return;
			value === undefined
				? localStorage.removeItem(key)
				: localStorage.setItem(key, JSON.stringify(value));
		},
	});
}
