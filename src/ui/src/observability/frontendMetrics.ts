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
		const timing = window.performance.timing;
		if (timing && timing.loadEventEnd && timing.navigationStart) {
			const loadTime = timing.loadEventEnd - timing.navigationStart;

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
		// eslint-disable-next-line no-console
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
}

export function trackWebSocketLatency(latencyMs: number): void {
	recordDistributionSafely(
		MetricName.WebSocketLatency,
		latencyMs,
		{
			tags: {
				metric_type: MetricType.Network,
			},
			unit: MetricUnit.Millisecond,
		},
	);
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

/**
 * Safely increments a metric if the provider supports it.
 * Handles the common pattern of checking for incrementMetric support and error handling.
 *
 * @param name The metric name to increment
 * @param options Optional metric options (tags, unit, value)
 * @param logger Optional logger for error reporting. If not provided, uses console.warn
 */
export function incrementMetricSafely(
	name: string,
	options?: IncrementMetricOptions,
	logger?: { warn: (message: string, error?: unknown) => void },
): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider && "incrementMetric" in provider) {
		try {
			(provider as IncrementMetricProvider).incrementMetric(name, options);
		} catch (e) {
			if (logger) {
				logger.warn("Failed to increment metric:", e);
			} else {
				// eslint-disable-next-line no-console
				console.warn("Failed to increment metric:", e);
			}
		}
	}
}

/**
 * Safely records a distribution metric if the provider supports it.
 * Handles the common pattern of checking for recordDistribution support and error handling.
 *
 * @param name The metric name to record
 * @param value The metric value to record
 * @param options Optional metric options (tags, unit)
 * @param logger Optional logger for error reporting. If not provided, uses console.warn
 */
export function recordDistributionSafely(
	name: string,
	value: number,
	options?: RecordDistributionOptions,
	logger?: { warn: (message: string, error?: unknown) => void },
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
			if (logger) {
				logger.warn("Failed to record metric:", e);
			} else {
				// eslint-disable-next-line no-console
				console.warn("Failed to record metric:", e);
			}
		}
	}
}
