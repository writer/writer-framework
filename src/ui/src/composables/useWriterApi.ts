import { WriterApi } from "@/writerApi";

export function useWriterApi(opts: { signal?: AbortSignal } = {}) {
	const apiBaseUrl =
		// @ts-expect-error use injected variable from Vite to specify the host on local env
		import.meta.env.VITE_WRITER_BASE_URL ?? window.location.origin;

	const writerApi = new WriterApi({
		...opts,
		baseUrl: apiBaseUrl,
	});

	return { writerApi, apiBaseUrl };
}
