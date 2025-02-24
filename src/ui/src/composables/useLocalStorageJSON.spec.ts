import { afterAll, beforeEach, describe, expect, it, Mock, vi } from "vitest";
import { useLocalStorageJSON } from "./useLocalStorageJSON";

describe(useLocalStorageJSON.name, () => {
	let localStorage: { getItem: Mock; setItem: Mock; removeItem: Mock };

	beforeEach(() => {
		localStorage = {
			getItem: vi.fn(),
			setItem: vi.fn(),
			removeItem: vi.fn(),
		};

		vi.stubGlobal("localStorage", localStorage);
	});

	afterAll(() => {
		vi.restoreAllMocks();
	});

	it("should get the value", () => {
		localStorage.getItem.mockReturnValue(JSON.stringify({ a: 1 }));

		const cache = useLocalStorageJSON("key");

		expect(cache.value).toStrictEqual({ a: 1 });
		expect(localStorage.getItem).toHaveBeenNthCalledWith(1, "key");
	});

	it("should set the value", () => {
		const cache = useLocalStorageJSON("key");

		cache.value = { b: 2 };
		expect(localStorage.setItem).toHaveBeenNthCalledWith(
			1,
			"key",
			JSON.stringify({ b: 2 }),
		);
	});

	it("should delete a non JSON value", () => {
		localStorage.getItem.mockReturnValue("{");

		const cache = useLocalStorageJSON("key");

		expect(cache.value).toBeUndefined();
		expect(localStorage.removeItem).toHaveBeenNthCalledWith(1, "key");
	});

	it("should delete an invalid value", () => {
		localStorage.getItem.mockReturnValue(1);

		const cache = useLocalStorageJSON("key", Array.isArray);

		expect(cache.value).toBeUndefined();
		expect(localStorage.removeItem).toHaveBeenNthCalledWith(1, "key");
	});
});
