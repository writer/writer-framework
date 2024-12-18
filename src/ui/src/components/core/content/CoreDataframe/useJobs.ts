import { useLogger } from "@/composables/useLogger";
import { shallowRef, ref, readonly } from "vue";

/**
 * A simple FIFO Job queue algorithm
 */
export function useJobs<T>(handler: (value: T) => Promise<void>) {
	const jobs = shallowRef<T[]>([]);
	const isRunning = ref(false);
	const logger = useLogger();

	async function run() {
		if (isRunning.value) return;

		isRunning.value = true;

		while (jobs.value.length) {
			const [job, ...rest] = jobs.value;

			try {
				await handler(job);
			} catch (error) {
				logger.error("Error during handling job", job, error);
			} finally {
				jobs.value = rest;
			}
		}

		isRunning.value = false;
	}

	function push(job: T) {
		jobs.value = [...jobs.value, job];
		if (!isRunning.value) return run();
	}

	return { push, isBusy: readonly(isRunning) };
}
