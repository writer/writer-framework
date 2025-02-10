import { useAssetContentType } from "./useAssetContentType";
import { beforeEach, describe, it, expect, Mock, vi } from "vitest";

describe(useAssetContentType.name, () => {
	let fetch: Mock;

	beforeEach(() => {
		fetch = vi.fn().mockResolvedValue({
			ok: true,
			headers: new Map([["Content-Type", "image/png"]]),
		});
		global.fetch = fetch;

		useAssetContentType().clearCache();
	});

	it("should handle error ", async () => {
		fetch.mockRejectedValue(new Error());
		const { fetchAssetContentType } = useAssetContentType();

		expect(await fetchAssetContentType("https://test.com")).toBeUndefined();
		expect(fetch).toHaveBeenCalledOnce();
	});

	it("should cache fetch call in sequential calls", async () => {
		const { fetchAssetContentType } = useAssetContentType();

		expect(await fetchAssetContentType("https://test.com")).toBe(
			"image/png",
		);
		expect(await fetchAssetContentType("https://test.com")).toBe(
			"image/png",
		);
		expect(fetch).toHaveBeenCalledOnce();
	});

	it("should cache fetch call in parrallel call", async () => {
		vi.useFakeTimers();

		fetch.mockResolvedValue(
			new Promise((res) =>
				setTimeout(
					() =>
						res({
							ok: true,
							headers: new Map([["Content-Type", "image/png"]]),
						}),
					3_000,
				),
			),
		);

		const { fetchAssetContentType } = useAssetContentType();

		const res1 = fetchAssetContentType("https://test.com");
		const res2 = fetchAssetContentType("https://test.com");

		vi.advanceTimersByTime(3_000);

		expect(await res1).toBe("image/png");
		expect(await res2).toBe("image/png");

		expect(fetch).toHaveBeenCalledOnce();
	});
});
