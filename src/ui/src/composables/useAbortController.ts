import { onBeforeUnmount } from "vue";

export function useAbortController() {
	const abortController = new AbortController();

	onBeforeUnmount(() => {
		abortController.abort();
	});

	return abortController;
}
