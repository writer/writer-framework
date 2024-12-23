const cacheUrlContentType = new Map<string, Promise<undefined | string>>();

/**
 * Do an HTTP `HEAD` call to get the `Content-Type` of an URL. Handle parrallel calls and use a cache mechanism.
 */
export function useAssetContentType() {
	function fetchAssetContentType(url: string) {
		const cachedValue = cacheUrlContentType.get(url);
		if (cachedValue !== undefined) return cachedValue;

		// we store the promise instead of the result to handle concurent calls
		const promise = fetch(url, { method: "HEAD" })
			.then((r) => {
				if (!r.ok) return undefined;
				return r.headers.get("Content-Type") || undefined;
			})
			.catch(() => undefined);

		cacheUrlContentType.set(url, promise);

		return promise;
	}

	function clearCache() {
		cacheUrlContentType.clear();
	}

	return { fetchAssetContentType, clearCache };
}
