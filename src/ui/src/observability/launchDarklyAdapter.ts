import type {
	IncrementMetricOptions,
	ObservabilityProvider,
	RecordDistributionOptions,
} from "./base";
import { LDObserve } from "@launchdarkly/observability";
import { isLaunchDarklyEnabled } from "@/utils/launchDarklyUtils";
import { useLogger } from "@/composables/useLogger";

const logger = useLogger();

export class LaunchDarklyAdapter implements ObservabilityProvider {
	private initialized = false;
	private ldObserve: typeof LDObserve;

	isEnabled(): boolean {
		// Check if LDObserve is available (for SDK-based initialization)
		const hasLDObserve = typeof LDObserve !== "undefined";

		// Check if client ID is configured (for client-side initialization)
		const hasClientId = isLaunchDarklyEnabled();

		return hasClientId || hasLDObserve;
	}

	getName(): string {
		return "launchdarkly";
	}

	async initialize(_app?: unknown, _router?: unknown): Promise<boolean> {
		if (this.initialized) {
			return true;
		}

		if (!this.isEnabled()) {
			logger.info(
				"LaunchDarkly client ID not provided, skipping LaunchDarkly initialization",
			);
			return false;
		}

		try {
			this.ldObserve = LDObserve;
			this.initialized = true;
			return true;
		} catch (error) {
			logger.warn(
				"Failed to initialize LaunchDarkly observability adapter:",
				error,
			);
			return false;
		}
	}

	incrementMetric(name: string, options?: IncrementMetricOptions): void {
		if (!this.initialized) return;
		try {
			this.ldObserve.recordIncr({
				name,
				attributes: options?.tags,
			});
		} catch (e) {
			logger.warn(`Failed to increment metric ${name}:`, e);
		}
	}

	recordDistribution(
		name: string,
		value: number,
		options?: RecordDistributionOptions,
	): void {
		if (!this.initialized) return;
		try {
			this.ldObserve.recordHistogram({
				name,
				value,
				attributes: options?.tags,
			});
		} catch (e) {
			logger.warn(`Failed to record distribution ${name}:`, e);
		}
	}

	setGauge(
		name: string,
		value: number,
		options?: RecordDistributionOptions,
	): void {
		if (!this.initialized) return;
		try {
			this.ldObserve.recordGauge({
				name,
				value,
				attributes: options?.tags,
			});
		} catch (e) {
			logger.warn(`Failed to set gauge ${name}:`, e);
		}
	}

	captureException(
		error: Error | string,
		context?: Record<string, unknown>,
	): void {
		if (!this.initialized) {
			return;
		}
		try {
			const errorObj = error instanceof Error ? error : new Error(error);

			const payload: Record<string, string> = {};
			if (context) {
				for (const [key, value] of Object.entries(context)) {
					payload[key] = String(value);
				}
			}

			if (context?.source) {
				payload.source = String(context.source);
			}
			if (context?.errorType) {
				payload.errorType = String(context.errorType);
			} else if (errorObj.name) {
				payload.errorType = errorObj.name;
			}

			this.ldObserve.recordError(
				errorObj,
				errorObj.message || String(error),
				Object.keys(payload).length > 0 ? payload : undefined,
			);
		} catch (e) {
			logger.warn("[LaunchDarkly] Failed to capture exception:", e);
		}
	}

	captureMessage(
		message: string,
		level?: "info" | "warning" | "error",
		context?: Record<string, unknown>,
	): void {
		if (!this.initialized) return;
		try {
			if (level === "error") {
				const payload: Record<string, string> = {};
				if (context) {
					for (const [key, value] of Object.entries(context)) {
						payload[key] = String(value);
					}
				}

				this.ldObserve.recordError(
					new Error(message),
					message,
					Object.keys(payload).length > 0 ? payload : undefined,
				);
			}
		} catch (e) {
			logger.warn("Failed to capture message:", e);
		}
	}

	/**
	 * Required by ObservabilityProvider interface, but LaunchDarkly manages
	 * user context differently. Context is set during client initialization
	 * via buildLDContext() and initializeLaunchDarkly() in launchDarklyClient.ts.
	 * This method is a no-op to satisfy the interface contract.
	 */
	setUser(_user: {
		id?: string;
		email?: string;
		username?: string;
		[key: string]: unknown;
	}): void {
		// LaunchDarkly context is set during client initialization
	}

	/**
	 * Required by ObservabilityProvider interface, but LaunchDarkly manages
	 * context differently. Context is set during client initialization
	 * via buildLDContext() and initializeLaunchDarkly() in launchDarklyClient.ts.
	 * This method is a no-op to satisfy the interface contract.
	 */
	setContext(_key: string, _value: unknown): void {
		// LaunchDarkly context is set during client initialization
	}
}
