/* eslint-disable no-console */

import { observabilityRegistry } from "@/observability";

export type ILogger = Pick<typeof console, "log" | "warn" | "info" | "error">;

export function useLogger(): ILogger {
	const provider = observabilityRegistry.getInitializedProvider();

	return {
		log: (...args: any[]) => {
			console.log(...args);
		},
		warn: (...args: any[]) => {
			console.warn(...args);
			if (provider && args.length > 0) {
				const message =
					typeof args[0] === "string" ? args[0] : String(args[0]);
				provider.captureMessage(message, "warning", {
					source: "logger",
					component: "useLogger",
					args: args.slice(1),
				});
			}
		},
		info: (...args: any[]) => {
			console.info(...args);
		},
		error: (...args: any[]) => {
			console.error(...args);
			if (provider && args.length > 0) {
				const error =
					args[0] instanceof Error
						? args[0]
						: new Error(String(args[0]));
				provider.captureException(error, {
					source: "logger",
					component: "useLogger",
					args: args.slice(1),
				});
			}
		},
	};
}
