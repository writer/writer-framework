interface Job {
	id: number;
	func: () => Promise<void>;
}
type Hook = (job: Job) => Promise<void>;

export function usePromiseQueue(
	hooks: {
		onJobExecuted?: Hook;
		onJobResolved?: Hook;
		onJobRejected?: Hook;
	} = {},
) {
	let nextId = 0;
	const jobs: Job[] = [];
	let isRunning = false;

	function add<T>(func: () => Promise<T>): Promise<T> {
		// eslint-disable-next-line no-async-promise-executor
		return new Promise(async (res, rej) => {
			async function callback() {
				try {
					const data = await func();
					res(data);
				} catch (e) {
					rej(e);
					throw e;
				}
			}

			const job = { func: callback, id: incrementNextId() };
			jobs.push(job);
			await run();
		});
	}

	async function run() {
		if (isRunning) return;
		isRunning = true;

		while (jobs.length > 0) {
			const job = jobs.shift();
			if (!job) continue;
			try {
				await job.func();
				if (hooks.onJobResolved) await hooks.onJobResolved(job);
			} catch {
				if (hooks.onJobRejected) await hooks.onJobRejected(job);
			} finally {
				if (hooks.onJobExecuted) await hooks.onJobExecuted(job);
			}
		}

		isRunning = false;
	}

	function incrementNextId() {
		return nextId++;
	}

	return { add };
}
