import { observabilityRegistry } from "./base";
import { useLogger } from "@/composables/useLogger";

const logger = useLogger();

type QueuedMetric =
	| {
			type: "increment";
			name: string;
			options?: { tags?: Record<string, string>; value?: number };
	  }
	| {
			type: "distribution";
			name: string;
			value: number;
			options?: { tags?: Record<string, string>; unit?: string };
	  }
	| {
			type: "gauge";
			name: string;
			value: number;
			options?: { tags?: Record<string, string>; unit?: string };
	  };

const metricQueue: QueuedMetric[] = [];
let isInitializing = false;
let initializationCheckInterval: ReturnType<typeof setInterval> | null = null;

export function flushMetricQueue(): void {
	if (metricQueue.length === 0) return;

	const provider = observabilityRegistry.getInitializedProvider();
	if (!provider) return;

	const queued = [...metricQueue];
	const queueSize = queued.length;
	metricQueue.length = 0;

	logger.log(
		`[LaunchDarkly] Flushing ${queueSize} queued metrics to observability`,
	);

	for (const metric of queued) {
		try {
			if (metric.type === "increment" && provider.incrementMetric) {
				provider.incrementMetric(metric.name, metric.options);
			} else if (
				metric.type === "distribution" &&
				provider.recordDistribution
			) {
				provider.recordDistribution(metric.name, metric.value, {
					tags: metric.options?.tags,
					unit: metric.options?.unit,
				});
			} else if (metric.type === "gauge" && provider.setGauge) {
				provider.setGauge(metric.name, metric.value, {
					tags: metric.options?.tags,
					unit: metric.options?.unit,
				});
			}
		} catch (e) {
			logger.warn(`Failed to flush queued metric ${metric.name}:`, e);
		}
	}

	logger.log(`[LaunchDarkly] Successfully flushed ${queueSize} metrics`);
}

function checkProviderReady(): void {
	const provider = observabilityRegistry.getInitializedProvider();
	if (provider) {
		isInitializing = false;
		if (initializationCheckInterval) {
			clearInterval(initializationCheckInterval);
			initializationCheckInterval = null;
		}
		flushMetricQueue();
	}
}

function startInitializationCheck(): void {
	if (initializationCheckInterval) return;

	isInitializing = true;
	initializationCheckInterval = setInterval(() => {
		checkProviderReady();
	}, 100);

	setTimeout(() => {
		if (initializationCheckInterval) {
			clearInterval(initializationCheckInterval);
			initializationCheckInterval = null;
			isInitializing = false;
		}
	}, 10000);
}

export const METRIC_NAMES = {
	WEBSOCKET_CONNECTED: "websocket_connected",
	WEBSOCKET_RECONNECTED: "websocket_reconnected",
	WEBSOCKET_RECONNECT_FAILED: "websocket_reconnect_failed",
	WEBSOCKET_CONNECT_DURATION: "websocket_connect_duration",
	WEBSOCKET_CONNECTION_FAILURE: "websocket_connection_failure",
	WEBSOCKET_MESSAGE_SEND_ERROR: "websocket_message_send_error",
	WEBSOCKET_UNEXPECTED_DISCONNECT: "websocket_unexpected_disconnect",
	WEBSOCKET_INVALID_MESSAGE: "websocket_invalid_message",
	WEBSOCKET_ABNORMAL_CLOSE: "websocket_abnormal_close",
	WEBSOCKET_CLOSE_ERROR: "websocket_close_error",
	FRONTEND_MESSAGE_SENT: "frontend_message_sent",
	FRONTEND_MESSAGE_ERROR: "frontend_message_error",
	FRONTEND_MESSAGE_DURATION: "frontend_message_duration",
	PAGE_LOAD_TIME: "page_load_time",
	COMPONENT_RENDER_TIME: "component_render_time",
	API_REQUEST_DURATION: "api_request_duration",
	API_REQUEST_COUNT: "api_request_count",
	USER_ACTION: "user_action",
	USER_CLICK: "user_click",
	USER_INPUT: "user_input",
	FEATURE_USAGE: "feature_usage",
	CONVERSION_EVENT: "conversion_event",
	ACTIVE_SESSIONS: "active_sessions",
	MEMORY_USAGE: "memory_usage",
	CPU_USAGE: "cpu_usage",
	ACTIVE_CONNECTIONS: "active_connections",
	QUEUE_SIZE: "queue_size",
} as const;

export function trackError(
	error: Error | string,
	errorType?: string,
	context?: Record<string, unknown>,
): void {
	try {
		const provider = observabilityRegistry.getInitializedProvider();
		if (!provider) {
			return;
		}

		const errorObj = error instanceof Error ? error : new Error(error);
		const errorContext = {
			...(context || {}),
			...(errorType ? { errorType } : {}),
		};

		provider.captureException(errorObj, errorContext);
	} catch (e) {
		logger.warn("Failed to track error:", e);
	}
}

export function incrementMetric(
	name: string,
	options?: { tags?: Record<string, string>; value?: number },
): void {
	try {
		const provider = observabilityRegistry.getInitializedProvider();
		if (provider?.incrementMetric) {
			provider.incrementMetric(name, {
				tags: options?.tags,
				value: options?.value,
			});
			return;
		}

		if (!isInitializing) {
			startInitializationCheck();
		}

		metricQueue.push({
			type: "increment",
			name,
			options,
		});
	} catch (e) {
		logger.warn(`Failed to increment metric ${name}:`, e);
	}
}

export function recordDistribution(
	name: string,
	value: number,
	options?: { tags?: Record<string, string>; unit?: string },
): void {
	try {
		const provider = observabilityRegistry.getInitializedProvider();
		if (provider?.recordDistribution) {
			provider.recordDistribution(name, value, {
				tags: options?.tags,
				unit: options?.unit,
			});
			return;
		}

		if (!isInitializing) {
			startInitializationCheck();
		}

		metricQueue.push({
			type: "distribution",
			name,
			value,
			options,
		});
	} catch (e) {
		logger.warn(`Failed to record distribution ${name}:`, e);
	}
}

export function setGauge(
	name: string,
	value: number,
	options?: { tags?: Record<string, string>; unit?: string },
): void {
	try {
		const provider = observabilityRegistry.getInitializedProvider();
		if (provider?.setGauge) {
			provider.setGauge(name, value, {
				tags: options?.tags,
				unit: options?.unit,
			});
			return;
		}

		if (!isInitializing) {
			startInitializationCheck();
		}

		metricQueue.push({
			type: "gauge",
			name,
			value,
			options,
		});
	} catch (e) {
		logger.warn(`Failed to set gauge ${name}:`, e);
	}
}

export function trackPageLoadTime(pageName: string, mode?: string): void {
	if (typeof window === "undefined" || !window.performance) {
		return;
	}

	const navigation = performance.getEntriesByType(
		"navigation",
	)[0] as PerformanceNavigationTiming;
	if (navigation) {
		const loadTime = navigation.loadEventEnd - navigation.fetchStart;
		if (loadTime <= 0) {
			return; // Page load not complete yet
		}
		recordDistribution(METRIC_NAMES.PAGE_LOAD_TIME, loadTime, {
			tags: { page: pageName, mode: mode || "unknown" },
			unit: "ms",
		});
	}
}

export function trackComponentRenderTime(
	componentName: string,
	renderTime: number,
	mode?: string,
): void {
	recordDistribution(METRIC_NAMES.COMPONENT_RENDER_TIME, renderTime, {
		tags: { component: componentName, mode: mode || "unknown" },
		unit: "ms",
	});
}

export function trackApiRequest(
	endpoint: string,
	duration: number,
	statusCode?: number,
	method?: string,
): void {
	const tags: Record<string, string> = {
		endpoint,
		status: statusCode?.toString() || "unknown",
	};
	if (method) {
		tags.method = method;
	}

	recordDistribution(METRIC_NAMES.API_REQUEST_DURATION, duration, {
		tags,
		unit: "ms",
	});

	incrementMetric(METRIC_NAMES.API_REQUEST_COUNT, {
		tags,
	});
}

export function trackUserAction(
	actionType: string,
	element?: string,
	additionalTags?: Record<string, string>,
): void {
	const tags: Record<string, string> = {
		action_type: actionType,
		...(element ? { element } : {}),
		...(additionalTags || {}),
	};

	incrementMetric(METRIC_NAMES.USER_ACTION, { tags });
}

export function trackUserClick(
	element: string,
	additionalTags?: Record<string, string>,
): void {
	trackUserAction("click", element, additionalTags);
	incrementMetric(METRIC_NAMES.USER_CLICK, {
		tags: { element, ...(additionalTags || {}) },
	});
}

export function trackUserInput(
	inputType: string,
	fieldName?: string,
	additionalTags?: Record<string, string>,
): void {
	const tags: Record<string, string> = {
		input_type: inputType,
		...(fieldName ? { field: fieldName } : {}),
		...(additionalTags || {}),
	};

	incrementMetric(METRIC_NAMES.USER_INPUT, { tags });
}

export function trackFeatureUsage(
	featureName: string,
	action: string,
	additionalTags?: Record<string, string>,
): void {
	incrementMetric(METRIC_NAMES.FEATURE_USAGE, {
		tags: {
			feature: featureName,
			action,
			...(additionalTags || {}),
		},
	});
}

export function trackConversionEvent(
	eventName: string,
	value?: number,
	additionalTags?: Record<string, string>,
): void {
	incrementMetric(METRIC_NAMES.CONVERSION_EVENT, {
		tags: {
			event: eventName,
			...(additionalTags || {}),
		},
		value,
	});
}

export function trackActiveSessions(
	count: number,
	additionalTags?: Record<string, string>,
): void {
	setGauge(METRIC_NAMES.ACTIVE_SESSIONS, count, {
		tags: additionalTags,
	});
}

export function trackMemoryUsage(
	memoryMB: number,
	additionalTags?: Record<string, string>,
): void {
	setGauge(METRIC_NAMES.MEMORY_USAGE, memoryMB, {
		tags: additionalTags,
		unit: "MB",
	});
}

export function trackCpuUsage(
	cpuPercent: number,
	additionalTags?: Record<string, string>,
): void {
	setGauge(METRIC_NAMES.CPU_USAGE, cpuPercent, {
		tags: additionalTags,
		unit: "percent",
	});
}

export function trackActiveConnections(
	count: number,
	additionalTags?: Record<string, string>,
): void {
	setGauge(METRIC_NAMES.ACTIVE_CONNECTIONS, count, {
		tags: additionalTags,
	});
}

export function trackQueueSize(
	size: number,
	queueName?: string,
	additionalTags?: Record<string, string>,
): void {
	const tags: Record<string, string> = {
		...(queueName ? { queue: queueName } : {}),
		...(additionalTags || {}),
	};

	setGauge(METRIC_NAMES.QUEUE_SIZE, size, { tags });
}
