import type { LDClient, LDContext } from "launchdarkly-js-client-sdk";
import { useLogger } from "@/composables/useLogger";
import {
	getLaunchDarklyClientId,
	getLaunchDarklyEnvironment,
} from "@/utils/launchDarklyUtils";

const LAUNCH_DARKLY_INIT_TIMEOUT = 5;

let ldClient: LDClient | null = null;
let isInitialized = false;
let initializationError: Error | null = null;

let globalErrorHandler: ((event: ErrorEvent) => void) | null = null;
let globalRejectionHandler: ((event: PromiseRejectionEvent) => void) | null =
	null;

const logger = useLogger();

export type LaunchDarklyContext = LDContext & {
	kind: "user";
	key: string;
	organizationId?: number | null;
	mode?: "run" | "edit";
	writerApplicationId?: string;
};

export function buildLDContext(
	sessionId: string | null,
	mode: "run" | "edit" | null,
	writerApplication:
		| {
				id?: string;
				organizationId?: string;
		  }
		| undefined,
): LaunchDarklyContext {
	let orgId: number | undefined;
	if (writerApplication?.organizationId) {
		const parsed = Number(writerApplication.organizationId);
		orgId = Number.isFinite(parsed) ? parsed : undefined;
	}

	let contextKey: string;
	if (sessionId) {
		contextKey = `session-${sessionId}`;
	} else if (orgId !== undefined) {
		contextKey = `org-${orgId}`;
	} else {
		contextKey = "anonymous";
	}

	return {
		kind: "user",
		key: contextKey,
		organizationId: orgId ?? null,
		mode: mode ?? undefined,
		writerApplicationId: writerApplication?.id,
	};
}

export async function initializeLaunchDarkly(
	context: LaunchDarklyContext,
	clientSideId?: string,
): Promise<void> {
	if (initializationError) {
		logger.warn(
			"LaunchDarkly skipping initialization - previous error",
			initializationError,
		);
		return;
	}

	if (isInitialized && ldClient) {
		return;
	}

	const clientId = clientSideId || getLaunchDarklyClientId();
	if (!clientId) {
		logger.warn(
			"LaunchDarkly no client ID available, skipping initialization",
		);
		return;
	}

	try {
		const { initialize } = await import("launchdarkly-js-client-sdk");
		const environment = getLaunchDarklyEnvironment();

		const backendOrigin =
			import.meta.env.VITE_BACKEND_ORIGIN ||
			(typeof window !== "undefined" && window.location.origin
				? `${window.location.origin}/api`
				: "/api");

		const observabilityModule = await import("@launchdarkly/observability");

		const Observability =
			(
				observabilityModule as {
					Observability?: new (...args: unknown[]) => unknown;
				}
			).Observability || observabilityModule.default;
		if (!Observability) {
			throw new Error(
				"Observability plugin not found. Available exports: " +
					Object.keys(observabilityModule).join(", "),
			);
		}

		const sessionReplayModule = await import(
			"@launchdarkly/session-replay"
		);

		const SessionReplay =
			(
				sessionReplayModule as {
					SessionReplay?: new (...args: unknown[]) => unknown;
				}
			).SessionReplay || sessionReplayModule.default;
		if (!SessionReplay) {
			throw new Error(
				"SessionReplay plugin not found. Available exports: " +
					Object.keys(sessionReplayModule).join(", "),
			);
		}

		const plugins = [
			new (Observability as new (config: unknown) => unknown)({
				serviceName: "writer-framework",
				serviceVersion:
					import.meta.env.WRITER_FRAMEWORK_VERSION || "unknown",
				environment: environment,
				networkRecording: {
					enabled: true,
					recordHeadersAndBody: true,
				},
				tracingOrigins: [backendOrigin],
			}),
			new (SessionReplay as new (config: unknown) => unknown)({
				privacySetting: "default",
			}),
		] as unknown[];

		ldClient = initialize(clientId, context, {
			bootstrap: "localStorage",
			application: {
				id: "writer-framework",
				version: import.meta.env.WRITER_FRAMEWORK_VERSION || "unknown",
			},
			plugins: plugins as never,
		});

		try {
			await ldClient.waitForInitialization(LAUNCH_DARKLY_INIT_TIMEOUT);
		} catch (_timeoutError) {
			throw new Error("LaunchDarkly initialization timeout");
		}

		isInitialized = true;
		initializationError = null; // Clear error on successful initialization

		try {
			const { observabilityRegistry, flushMetricQueue } = await import(
				"@/observability"
			);
			await observabilityRegistry.initializeProvider("launchdarkly");
			flushMetricQueue();
		} catch (_e) {
			logger.warn("Failed to initialize observability provider:", _e);
		}

		ldClient.on("error", async (error) => {
			logger.warn("LaunchDarkly SDK error", error);
			try {
				const { observabilityRegistry } = await import(
					"@/observability"
				);
				const provider = observabilityRegistry.getInitializedProvider();
				if (provider?.captureException) {
					const errorObj =
						error instanceof Error
							? error
							: new Error(String(error));
					provider.captureException(errorObj, {
						source: "launchdarkly-sdk",
						type: "sdk_error",
					});
					logger.log(
						"[LaunchDarkly] Captured SDK error to observability",
						{
							error: errorObj.message,
							source: "launchdarkly-sdk",
						},
					);
				}
			} catch {
				// Ignore if observability not available
			}
		});

		if (typeof window !== "undefined") {
			const captureErrorToLD = async (
				error: Error,
				context?: Record<string, unknown>,
			) => {
				try {
					const { observabilityRegistry } = await import(
						"@/observability"
					);
					const provider =
						observabilityRegistry.getInitializedProvider();
					if (provider?.captureException) {
						provider.captureException(error, context);
						logger.log(
							"[LaunchDarkly] Captured error to observability",
							{
								error: error.message,
								source: context?.source,
							},
						);
						return true;
					}
				} catch {
					// Ignore if observability not available
				}
				return false;
			};

			if (globalErrorHandler) {
				window.removeEventListener("error", globalErrorHandler);
			}
			if (globalRejectionHandler) {
				window.removeEventListener(
					"unhandledrejection",
					globalRejectionHandler,
				);
			}

			globalErrorHandler = async (event: ErrorEvent) => {
				await captureErrorToLD(
					event.error || new Error(event.message),
					{
						source: "global-error-handler",
						filename: event.filename,
						lineno: event.lineno,
						colno: event.colno,
					},
				);
			};

			globalRejectionHandler = async (event: PromiseRejectionEvent) => {
				const error =
					event.reason instanceof Error
						? event.reason
						: new Error(String(event.reason));
				await captureErrorToLD(error, {
					source: "unhandled-rejection",
					promise: true,
				});
			};

			window.addEventListener("error", globalErrorHandler);
			window.addEventListener(
				"unhandledrejection",
				globalRejectionHandler,
			);
		}
	} catch (error) {
		initializationError = error as Error;
		logger.warn("LaunchDarkly initialization failed", error);
		ldClient = null;
		isInitialized = false;
		throw error;
	}
}

export function getFlagValue(flagKey: string, defaultValue: boolean): boolean {
	try {
		if (ldClient && isInitialized) {
			return ldClient.variation(flagKey, defaultValue);
		}
	} catch (error) {
		logger.warn(
			`LaunchDarkly flag evaluation failed for ${flagKey}`,
			error,
		);
	}
	return defaultValue;
}

export function isLDInitialized(): boolean {
	return isInitialized && ldClient !== null;
}

export function setupFlagChangeListener(
	onFlagsChange: (flags: string[]) => void,
): void {
	if (!ldClient || !isInitialized) {
		return;
	}

	try {
		ldClient.on("change", (settings) => {
			try {
				const activeFlags = Object.keys(settings).filter((k) => {
					const flagValue = settings[k];
					const value =
						flagValue &&
						typeof flagValue === "object" &&
						"current" in flagValue
							? (flagValue as { current: unknown }).current
							: flagValue;
					return value !== undefined && Boolean(value);
				});
				onFlagsChange(activeFlags);
			} catch (e) {
				logger.error("LaunchDarkly flag change handler error", e);
			}
		});
	} catch (error) {
		logger.warn(
			"Failed to set up LaunchDarkly flag change listener",
			error,
		);
	}
}

if (typeof window !== "undefined") {
	(window as { __LD_CLIENT_MODULE__?: unknown }).__LD_CLIENT_MODULE__ = {
		isLDInitialized: () => isInitialized && ldClient !== null,
		getFlagValue: (flagKey: string, defaultValue: boolean) => {
			if (!isInitialized || !ldClient) {
				return defaultValue;
			}
			try {
				return ldClient.variation(flagKey, defaultValue);
			} catch (error) {
				logger.warn(
					`LaunchDarkly flag evaluation failed for ${flagKey}`,
					error,
				);
				return defaultValue;
			}
		},
	};
}
