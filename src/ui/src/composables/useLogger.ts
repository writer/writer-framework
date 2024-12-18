/* eslint-disable no-console */

/**
 * A simple abstraction to use logger in the application. For the moment, it's just a proxy to `console`, but it can be plugged to any library later.
 */
export function useLogger(): Pick<
	typeof console,
	"log" | "warn" | "info" | "error"
> {
	return {
		log: console.log,
		warn: console.warn,
		info: console.info,
		error: console.error,
	};
}
