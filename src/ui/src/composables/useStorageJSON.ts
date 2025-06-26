import { computed, shallowRef } from "vue";

type Validator<T> = (value: T) => boolean;

/**
 * Get/Set the JSON object in localStorage
 * @param validator Validate that the data has a given shape; remove the localStorage value if the validator returns `false`.
 */
export function useLocalStorageJSON<T>(key: string, validator?: Validator<T>) {
	return useStorageJSON(window.localStorage, key, validator);
}

/**
 * Get/Set the JSON object in sessionStorage
 * @param validator Validate that the data has a given shape; remove the sessionStorage value if the validator returns `false`.
 */
export function useSessionStorageJSON<T>(
	key: string,
	validator?: Validator<T>,
) {
	return useStorageJSON(window.sessionStorage, key, validator);
}

function useStorageJSON<T>(
	storage: Storage | undefined,
	key: string,
	validator?: Validator<T>,
) {
	const actualValue = shallowRef<T | undefined>(get());

	function get() {
		if (!storage) return undefined;

		const value = storage.getItem(key);
		if (!value) return undefined;

		try {
			const data = JSON.parse(value);
			if (validator?.(data) === false) {
				storage.removeItem(key);
				return undefined;
			}
			return data;
		} catch {
			storage.removeItem(key);
			return undefined;
		}
	}

	return computed<T | undefined>({
		get() {
			return actualValue.value;
		},
		set(value) {
			actualValue.value = value;
			if (!storage) return undefined;
			value === undefined
				? storage.removeItem(key)
				: storage.setItem(key, JSON.stringify(value));
		},
	});
}
