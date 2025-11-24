import { ObservabilityRegistry } from "./base";
import { SentryAdapter } from "./sentryAdapter";

export type { ObservabilityProvider } from "./base";
export { ObservabilityRegistry } from "./base";
export { SentryAdapter } from "./sentryAdapter";

export const observabilityRegistry = new ObservabilityRegistry();

try {
	observabilityRegistry.register("sentry", new SentryAdapter());
} catch (error) {
	// eslint-disable-next-line no-console
	console.debug("Sentry adapter not available:", error);
}
