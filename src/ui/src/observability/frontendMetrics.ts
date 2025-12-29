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
	metricQueue.length = 0;

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
