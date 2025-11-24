import { observabilityRegistry } from "./index";

export function trackPageLoadTime(): void {
	if (typeof window === "undefined" || !window.performance) {
		return;
	}

	try {
		const timing = window.performance.timing;
		if (timing && timing.loadEventEnd && timing.navigationStart) {
			const loadTime = timing.loadEventEnd - timing.navigationStart;

			const provider = observabilityRegistry.getInitializedProvider();
			if (provider && "recordDistribution" in provider) {
				(
					provider as {
						recordDistribution: (
							name: string,
							value: number,
							options?: {
								tags?: Record<string, string>;
								unit?: string;
							},
						) => void;
					}
				).recordDistribution("frontend_page_load_time_ms", loadTime, {
					tags: {
						metric_type: "performance",
					},
					unit: "millisecond",
				});
			}
		}
	} catch (e) {
		// eslint-disable-next-line no-console
		console.warn("Failed to track page load time:", e);
	}
}

export function trackError(error: Error, errorType?: string): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "incrementMetric" in provider) {
		try {
			(
				provider as {
					incrementMetric: (
						name: string,
						options?: {
							tags?: Record<string, string>;
							unit?: string;
							value?: number;
						},
					) => void;
				}
			).incrementMetric("frontend_errors_total", {
				tags: {
					error_type: errorType || error.name || "unknown",
					error_message:
						error.message?.substring(0, 100) || "unknown",
				},
				unit: "none",
			});
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn("Failed to track error metric:", e);
		}
	}
}

export function trackWebSocketLatency(latencyMs: number): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "recordDistribution" in provider) {
		try {
			(
				provider as {
					recordDistribution: (
						name: string,
						value: number,
						options?: {
							tags?: Record<string, string>;
							unit?: string;
						},
					) => void;
				}
			).recordDistribution("websocket_latency_ms", latencyMs, {
				tags: {
					metric_type: "network",
				},
				unit: "millisecond",
			});
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn("Failed to track websocket latency:", e);
		}
	}
}

export function trackRouteChange(route: string): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "incrementMetric" in provider) {
		try {
			(
				provider as {
					incrementMetric: (
						name: string,
						options?: {
							tags?: Record<string, string>;
							unit?: string;
							value?: number;
						},
					) => void;
				}
			).incrementMetric("frontend_route_changes_total", {
				tags: {
					route: route || "unknown",
				},
				unit: "none",
			});
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn("Failed to track route change:", e);
		}
	}
}

export function trackInteractionDuration(
	actionType: string,
	durationMs: number,
): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "recordDistribution" in provider) {
		try {
			(
				provider as {
					recordDistribution: (
						name: string,
						value: number,
						options?: {
							tags?: Record<string, string>;
							unit?: string;
						},
					) => void;
				}
			).recordDistribution(
				"frontend_interaction_duration_ms",
				durationMs,
				{
					tags: {
						action_type: actionType,
					},
					unit: "millisecond",
				},
			);
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn("Failed to track interaction duration:", e);
		}
	}
}
