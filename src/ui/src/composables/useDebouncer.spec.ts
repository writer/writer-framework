import { describe, it, vi, expect, beforeAll, afterAll } from "vitest";
import { useDebouncer } from "./useDebouncer";

describe(useDebouncer.name, () => {
	beforeAll(() => {
		vi.useFakeTimers();
	});

	afterAll(() => {
		vi.useRealTimers();
	});

	it("should call the callback one time", () => {
		const callback = vi.fn();

		const callbackDebounced = useDebouncer(callback, 1_000);

		callbackDebounced();
		callbackDebounced();
		vi.advanceTimersByTime(1_000);
		expect(callback).toHaveBeenCalledTimes(1);

		callbackDebounced();
		vi.advanceTimersByTime(500);
		expect(callback).toHaveBeenCalledTimes(1);

		callbackDebounced();
		vi.advanceTimersByTime(1_000);
		expect(callback).toHaveBeenCalledTimes(2);
	});
});
