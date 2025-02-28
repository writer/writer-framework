import { computed } from "vue";

/**
 * Get/Set the JSON object in localStorage
 * @param validator validate that the data has a given shape, remote the localStorage value if returns `false`
 */
export function useLocalStorageJSON<T>(
	key: string,
	validator?: (value: T) => boolean,
) {
	return computed<T | undefined>({
		get() {
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
		},
		set(value) {
			value === undefined
				? localStorage.removeItem(key)
				: localStorage.setItem(key, JSON.stringify(value));
		},
	});
}
