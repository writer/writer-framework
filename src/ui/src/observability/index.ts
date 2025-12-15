import { ObservabilityRegistry } from "./base";
import { LaunchDarklyAdapter } from "./launchDarklyAdapter";

export type { ObservabilityProvider } from "./base";
export { ObservabilityRegistry } from "./base";
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

export const observabilityRegistry = new ObservabilityRegistry();

try {
	observabilityRegistry.register("launchdarkly", new LaunchDarklyAdapter());
} catch (error) {
	// eslint-disable-next-line no-console
	console.debug("LaunchDarkly adapter not available:", error);
}
