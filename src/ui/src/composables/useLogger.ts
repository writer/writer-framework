/* eslint-disable no-console */

export type ILogger = Pick<typeof console, "log" | "warn" | "info" | "error">;

/**
 * A simple abstraction to use logger in the application. For the moment, it's just a proxy to `console`, but it can be plugged to any library later.
 */
export function useLogger(): ILogger {
	return {
		log: console.log,
		warn: console.warn,
		info: console.info,
		error: console.error,
	};
}
