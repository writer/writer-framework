import { WriterApiUserProfile, WriterApiUser } from "@/writerApi";
import { ComputedRef, onMounted, readonly, ref, shallowRef, watch } from "vue";
import { useWriterApi } from "./useWriterApi";

let fetchCurrentUser: Promise<WriterApiUserProfile> | undefined;

export async function fetchWriterApiCurrentUserProfile(
	writerApi = useWriterApi().writerApi,
) {
	fetchCurrentUser ??= writerApi.fetchUserProfile();
	return await fetchCurrentUser;
}

export function useWriterApiCurrentUserProfile(
	writerApi = useWriterApi().writerApi,
) {
	const user = shallowRef<WriterApiUserProfile | undefined>();
	const error = shallowRef();
	const isLoading = ref(false);

	async function fetchUser() {
		error.value = undefined;
		isLoading.value = true;
		try {
			user.value = await fetchWriterApiCurrentUserProfile(writerApi);
		} catch (e) {
			error.value = e;
			user.value = undefined;
		} finally {
			isLoading.value = false;
		}
	}

	onMounted(fetchUser);

	return {
		user: readonly(user),
		isLoading: readonly(isLoading),
		error: readonly(error),
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
