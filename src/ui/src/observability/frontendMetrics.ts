/* eslint-disable no-console */
import { observabilityRegistry } from "./index";

export enum MetricName {
	FrontendPageLoadTime = "frontend_page_load_time_ms",
	FrontendErrorsTotal = "frontend_errors_total",
	WebSocketLatency = "websocket_latency_ms",
	FrontendRouteChangesTotal = "frontend_route_changes_total",
	FrontendInteractionDuration = "frontend_interaction_duration_ms",
	WebSocketMessageDuration = "websocket.message_duration",
	WebSocketMessageError = "websocket.message_error",
	ComponentDeleted = "component.deleted",
	ComponentAdded = "component.added",
}

export enum MetricType {
	Performance = "performance",
	Network = "network",
}

export enum MetricUnit {
	Millisecond = "millisecond",
	None = "none",
}

export interface RecordDistributionOptions {
	tags?: Record<string, string>;
	unit?: string;
}

export interface IncrementMetricOptions {
	tags?: Record<string, string>;
	unit?: string;
	value?: number;
}

export type RecordDistributionProvider = {
	recordDistribution: (
		name: string,
		value: number,
		options?: RecordDistributionOptions,
	) => void;
};

export type IncrementMetricProvider = {
	incrementMetric: (name: string, options?: IncrementMetricOptions) => void;
};

export function trackPageLoadTime(): void {
	if (typeof window === "undefined" || !window.performance) {
		return;
	}

	try {
		let loadTime: number | null = null;

		const navigationEntries = performance.getEntriesByType(
			"navigation",
		) as PerformanceNavigationTiming[];
		if (navigationEntries.length > 0) {
			const entry = navigationEntries[0];
			if (entry.loadEventEnd && entry.startTime) {
				loadTime = entry.loadEventEnd - entry.startTime;
			} else if (entry.duration) {
				loadTime = entry.duration;
			}
		}

		if (loadTime !== null) {
			recordDistributionSafely(
				MetricName.FrontendPageLoadTime,
				loadTime,
				{
					tags: {
						metric_type: MetricType.Performance,
					},
					unit: MetricUnit.Millisecond,
				},
			);
		}
	} catch (e) {
		console.warn("Failed to track page load time:", e);
	}
}

export function trackError(error: Error, errorType?: string): void {
	incrementMetricSafely(MetricName.FrontendErrorsTotal, {
		tags: {
			error_type: errorType || error.name || "unknown",
			error_message: error.message?.substring(0, 100) || "unknown",
		},
		unit: MetricUnit.None,
	});

	const provider = observabilityRegistry.getInitializedProvider();
	if (provider) {
		try {
			provider.captureException(error, {
				source: "global_error_handler",
				error_type: errorType || error.name || "unknown",
			});
		} catch (e) {
			console.warn("Failed to send error to Sentry:", e);
		}
	}
}

export function trackWebSocketLatency(latencyMs: number): void {
	recordDistributionSafely(MetricName.WebSocketLatency, latencyMs, {
		tags: {
			metric_type: MetricType.Network,
		},
		unit: MetricUnit.Millisecond,
	});
}

let lastTrackedRoute: string | null = null;

export function trackRouteChange(route: string): void {
	const normalizedRoute = route || "unknown";

	if (lastTrackedRoute === normalizedRoute) {
		return;
	}

	lastTrackedRoute = normalizedRoute;

	incrementMetricSafely(MetricName.FrontendRouteChangesTotal, {
		tags: {
			route: normalizedRoute,
		},
		unit: MetricUnit.None,
	});
}

export function trackInteractionDuration(
	actionType: string,
	durationMs: number,
): void {
	recordDistributionSafely(
		MetricName.FrontendInteractionDuration,
		durationMs,
		{
			tags: {
				action_type: actionType,
			},
			unit: MetricUnit.Millisecond,
		},
	);
}

export function incrementMetricSafely(
	name: string,
	options?: IncrementMetricOptions,
): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "incrementMetric" in provider) {
		try {
			(provider as IncrementMetricProvider).incrementMetric(
				name,
				options,
			);
		} catch (e) {
			console.warn("Failed to increment metric:", e);
		}
	}
}

export function recordDistributionSafely(
	name: string,
	value: number,
	options?: RecordDistributionOptions,
): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "recordDistribution" in provider) {
		try {
			(provider as RecordDistributionProvider).recordDistribution(
				name,
				value,
				options,
			);
		} catch (e) {
			console.warn("Failed to record metric:", e);
		}
	}
}
