import { WriterApiUserProfile, WriterApiUser } from "@/writerApi";
import { ComputedRef, readonly, ref, shallowRef, watch } from "vue";
import { useWriterApi } from "./useWriterApi";

export function useWriterApiCurrentUserProfile(
	writerApi = useWriterApi().writerApi,
) {
	let cache: WriterApiUserProfile | undefined;

	return async () => {
		if (cache) return cache;

		cache = await writerApi.fetchUserProfile();
		return cache;
	};
}

const fetchUserByIdPromises: Record<number, Promise<WriterApiUser>> = {};

export function useWriterApiUserProfile(
	userId: ComputedRef<number>,
	writerApi = useWriterApi().writerApi,
) {
	const user = shallowRef<WriterApiUser | undefined>();
	const error = shallowRef();
	const isLoading = ref(false);

	async function fetchUser(id: number) {
		error.value = undefined;
		isLoading.value = true;
		try {
			fetchUserByIdPromises[id] ??= writerApi.fetchUserById(id);
			user.value = await fetchUserByIdPromises[id];
		} catch (e) {
			error.value = e;
			user.value = undefined;
		} finally {
			isLoading.value = false;
		}
	}

	watch(userId, fetchUser, { immediate: true });

	return {
		user: readonly(user),
		isLoading: readonly(isLoading),
		error: readonly(error),
	};
}
