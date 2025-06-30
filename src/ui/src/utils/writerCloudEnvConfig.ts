type WriterAppConfig = Record<string, unknown>;

declare global {
	interface Window {
		__WRITER_APP_CONFIG__: WriterAppConfig;
	}
}

let cache: WriterAppConfig | undefined = undefined;

function isObject(v: unknown) {
	return typeof v === "object" && v !== null;
}

async function getWriterCloudEnvConfigText() {
	const apiBaseUrl =
		import.meta.env.VITE_WRITER_BASE_URL ?? window.location.origin;
	const url = new URL("/env/config.js", apiBaseUrl);

	try {
		const res = await fetch(url, { credentials: "include" });
		return res.text();
	} catch {
		return undefined;
	}
}

/**
 * Load the Writer's env variables from `/env/config.js`. It safely fails if the URL doesn't exist (like for local or self-hosted mode).
 */
export async function getWriterCloudEnvConfig(
	disableCache = false,
): Promise<WriterAppConfig> {
	if (disableCache) {
		cache = undefined;
	}
	if (cache) return cache;

	const javascriptContent = await getWriterCloudEnvConfigText();
	if (!javascriptContent) {
		cache = {};
		return cache;
	}

	const blob = new Blob([javascriptContent], {
		type: "application/javascript",
	});
	const blobUrl = URL.createObjectURL(blob);

	try {
		await import(/* @vite-ignore */ blobUrl);
	} catch {
		cache = {};
		return cache;
	} finally {
		// Clean up the blob URL after import
		URL.revokeObjectURL(blobUrl);
	}

	if (isObject(window.__WRITER_APP_CONFIG__)) {
		cache = window.__WRITER_APP_CONFIG__;
	} else if (typeof window.__WRITER_APP_CONFIG__ === "string") {
		try {
			cache = JSON.parse(
				atob(window.__WRITER_APP_CONFIG__),
			) as WriterAppConfig;
		} catch {
			cache = {};
		}
	} else {
		cache = {};
	}

	return cache;
}
