/* eslint-disable no-console */

import { observabilityRegistry } from "@/observability";

export type ILogger = Pick<typeof console, "log" | "warn" | "info" | "error">;

export function useLogger(): ILogger {
	const provider = observabilityRegistry.getInitializedProvider();

	return {
		log: console.log,
		info: console.info,
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
