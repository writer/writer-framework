import { observabilityRegistry } from "./base";
import { LaunchDarklyAdapter } from "./launchDarklyAdapter";

export type { ObservabilityProvider } from "./base";
export { ObservabilityRegistry, observabilityRegistry } from "./base";
export { LaunchDarklyAdapter } from "./launchDarklyAdapter";
export {
	trackError,
	incrementMetric,
	recordDistribution,
	setGauge,
	METRIC_NAMES,
	trackPageLoadTime,
	trackComponentRenderTime,
	trackApiRequest,
	trackUserAction,
	trackUserClick,
	trackUserInput,
	trackFeatureUsage,
	trackConversionEvent,
	trackActiveSessions,
	trackMemoryUsage,
	trackCpuUsage,
	trackActiveConnections,
	trackQueueSize,
	flushMetricQueue,
} from "./frontendMetrics";

// Re-export the singleton instance (created in base.ts to avoid circular dependencies)

try {
	observabilityRegistry.register("launchdarkly", new LaunchDarklyAdapter());
} catch (error) {
	// eslint-disable-next-line no-console
	console.debug("LaunchDarkly adapter not available:", error);
}
