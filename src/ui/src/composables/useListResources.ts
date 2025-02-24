import { generateCore } from "@/core";
import { readonly, ref, shallowRef } from "vue";
import { useLocalStorageJSON } from "./useLocalStorageJSON";

export function useListResources<T>(
	wf: ReturnType<typeof generateCore>,
	type: string,
) {
	const isLoading = ref(false);
	const error = ref();

	const cache = useLocalStorageJSON<T[]>(
		`useListResources(${type})`,
		Array.isArray,
	);

	const data = shallowRef<T[]>(cache.value ?? []);

	async function load() {
		isLoading.value = true;
		error.value = undefined;
		try {
			data.value = await wf.sendListResourcesRequest<T>(type);
			cache.value = data.value;
		} catch (e) {
			error.value = e;
			data.value = [];
		} finally {
			isLoading.value = false;
		}
	}

	return {
		data: readonly(data),
		isLoading: readonly(isLoading),
		error: readonly(error),
		load,
	};
}
