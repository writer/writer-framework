import { describe, it, expect, vi } from "vitest";
import { usePromiseQueue } from "./usePromiseQueue";
import { flushPromises } from "@vue/test-utils";

describe(usePromiseQueue.name, () => {
	it("should handle sequential functions", async () => {
		const onJobExecuted = vi.fn();

		let counter = 0;
		async function func() {
			counter++;
			return counter;
		}

		const queue = usePromiseQueue({ onJobExecuted });
		await expect(queue.add(func)).resolves.toBe(1);
		await expect(queue.add(func)).resolves.toBe(2);
		await expect(queue.add(func)).resolves.toBe(3);

		expect(onJobExecuted).toHaveBeenCalledTimes(3);
	});

	it("should handle error functions", async () => {
		const onJobRejected = vi.fn();
		const onJobExecuted = vi.fn();

		let counter = 0;

		async function func() {
			counter++;
			return counter;
		}
		async function throws() {
			throw Error();
		}

		const queue = usePromiseQueue({ onJobRejected, onJobExecuted });
		await expect(queue.add(throws)).rejects.toBeInstanceOf(Error);
		await expect(queue.add(throws)).rejects.toBeInstanceOf(Error);
		await expect(queue.add(func)).resolves.toBe(1);

		await flushPromises();
		expect(onJobRejected).toHaveBeenCalledTimes(2);
		expect(onJobExecuted).toHaveBeenCalledTimes(3);
	});
});
