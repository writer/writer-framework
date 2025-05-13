type WriterAppConfig = Record<string, unknown>;

declare global {
	interface Window {
		__WRITER_APP_CONFIG__: WriterAppConfig;
	}
}

function isObject(v: unknown) {
	return typeof v === "object" && v !== null;
}

/**
 * Load the Writer's env variables from `/env/config.js`. It safely fails if the URL doesn't exist (like for local or self-hosted mode).
 */
export async function getWriterCloudEnvConfig(): Promise<WriterAppConfig> {
	if (isObject(window.__WRITER_APP_CONFIG__))
		return window.__WRITER_APP_CONFIG__;

	const apiBaseUrl =
		// @ts-expect-error use injected variable from Vite to specify the host on local env
		import.meta.env.VITE_WRITER_BASE_URL ?? window.location.origin;
	const url = new URL("/env/config.js", apiBaseUrl);

	try {
		await import(/* @vite-ignore */ url.toString());

		return isObject(window.__WRITER_APP_CONFIG__)
			? window.__WRITER_APP_CONFIG__
			: {};
	} catch {
		// could not load the config, simply ignore
		return {};
	}
}
