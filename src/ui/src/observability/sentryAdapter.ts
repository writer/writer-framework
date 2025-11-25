/* eslint-disable no-console */
import type { ObservabilityProvider } from "./base";
import { trackRouteChange } from "./frontendMetrics";
import { getParsedHash } from "@/core/navigation";
import type * as SentryVue from "@sentry/vue";

export const SENTRY_DSN_ENV = "VITE_SENTRY_DSN";

interface SentryApi {
	captureException: typeof SentryVue.captureException;
	captureMessage: typeof SentryVue.captureMessage;
	setUser: typeof SentryVue.setUser;
	setContext: typeof SentryVue.setContext;
}

interface SentryMetricData {
	attributes?: Record<string, string>;
	unit?: string;
}

interface BrowserTracingOptions {
	router?: unknown;
	tracingOrigins?: (string | RegExp)[];
	routeLabel?: "name" | "path";
}

interface AppMetadata {
	agent_id?: string;
	organization_id?: string;
	mode?: string;
	[key: string]: unknown;
}

interface SentryMetricOptions {
	tags?: Record<string, string>;
	unit?: string;
}

interface SentryIncrementMetricOptions extends SentryMetricOptions {
	value?: number;
}

interface RuntimeContext {
	url: string;
	userAgent: string;
	[key: string]: unknown;
}

interface SentryMetrics {
	count: (name: string, value?: number, data?: SentryMetricData) => void;
	distribution: (
		name: string,
		value: number,
		data?: SentryMetricData,
	) => void;
	gauge: (name: string, value: number, data?: SentryMetricData) => void;
}

interface SentryModule {
	init: (config: SentryInitConfig) => void;
	captureException: SentryApi["captureException"];
	captureMessage: SentryApi["captureMessage"];
	setUser: SentryApi["setUser"];
	setContext: SentryApi["setContext"];
	setTag?: (key: string, value: string) => void;
	metrics?: SentryMetrics;
	vueIntegration?: (options?: { app?: unknown }) => unknown;
	browserTracingIntegration?: (options?: BrowserTracingOptions) => unknown;
	BrowserTracing?: new (options?: BrowserTracingOptions) => unknown;
}

interface SentryInitConfig {
	dsn: string;
	environment: string;
	tracesSampleRate: number;
	replay?: {
		sampleRate: number;
	};
	enableMetrics?: boolean;
	app?: unknown;
	integrations?: unknown[];
}

type BrowserTracingFunction = (options?: BrowserTracingOptions) => unknown;
type BrowserTracingClass = new (options?: BrowserTracingOptions) => unknown;
type BrowserTracingIntegration = BrowserTracingFunction | BrowserTracingClass;

export class SentryAdapter implements ObservabilityProvider {
	private initialized = false;
	private sentry: SentryApi | null = null;
	private metrics: SentryMetrics | null = null;
	private sentryModule: SentryModule | null = null;
	private app: unknown = null;
	private router: unknown = null;

	isEnabled(): boolean {
		return !!import.meta.env[SENTRY_DSN_ENV];
	}

	getName(): string {
		return "sentry";
	}

	async initialize(app?: unknown, router?: unknown): Promise<boolean> {
		if (this.initialized) {
			return true;
		}

		if (!this.isEnabled()) {
			console.info(
				"Sentry DSN not provided, skipping Sentry initialization",
			);
			return false;
		}

		if (router) {
			this.router = router;
		}

		try {
			const dsn = import.meta.env[SENTRY_DSN_ENV];
			if (!dsn) {
				console.info(
					"Sentry DSN not provided, skipping Sentry initialization",
				);
				return false;
			}

			let SentryModule: SentryModule;
			try {
				const sentryImport = await import(
					/* @vite-ignore */ "@sentry/vue"
				);
				SentryModule = sentryImport as unknown as SentryModule;
			} catch (importError) {
				console.warn(
					"Failed to import @sentry/vue package. Make sure it's installed: npm install @sentry/vue",
					importError,
				);
				return false;
			}

			const {
				init,
				captureException,
				captureMessage,
				setUser,
				setContext,
			} = SentryModule;

			const integrations: unknown[] = [];

			if (SentryModule.vueIntegration) {
				integrations.push(
					SentryModule.vueIntegration({
						app: app || undefined,
					}),
				);
			}

			let browserTracingIntegration: BrowserTracingIntegration | null =
				null;
			if (SentryModule.browserTracingIntegration) {
				browserTracingIntegration =
					SentryModule.browserTracingIntegration;
			} else if (SentryModule.BrowserTracing) {
				browserTracingIntegration = SentryModule.BrowserTracing;
			} else {
				try {
					const browserModule = (await import(
						/* @vite-ignore */ "@sentry/browser"
					)) as {
						browserTracingIntegration?: BrowserTracingIntegration;
					};
					if (browserModule.browserTracingIntegration) {
						browserTracingIntegration =
							browserModule.browserTracingIntegration;
					}
				} catch {
					console.warn(
						"BrowserTracing not available. Performance monitoring will be limited.",
					);
				}
			}

			const tracesSampleRate = parseFloat(
				import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || "0.1",
			);
			const replaySampleRate = parseFloat(
				import.meta.env.VITE_SENTRY_REPLAY_SAMPLE_RATE || "0.1",
			);

			const initConfig: SentryInitConfig = {
				dsn,
				environment: "production",
				tracesSampleRate,
				replay: {
					sampleRate: replaySampleRate,
				},
				enableMetrics: true,
			};

			if (app) {
				initConfig.app = app;
				this.app = app;
			}

			if (browserTracingIntegration) {
				const tracingOptions: BrowserTracingOptions = {
					tracingOrigins: ["localhost", /^\//],
				};

				if (this.router) {
					tracingOptions.router = this.router;
					tracingOptions.routeLabel = "path";
				}

				if (
					typeof browserTracingIntegration === "function" &&
					!browserTracingIntegration.prototype
				) {
					const integration =
						browserTracingIntegration as BrowserTracingFunction;
					integrations.push(integration(tracingOptions));
				} else {
					const IntegrationClass =
						browserTracingIntegration as BrowserTracingClass;
					integrations.push(new IntegrationClass(tracingOptions));
				}
			}

			if (integrations.length > 0) {
				initConfig.integrations = integrations;
			}

			init(initConfig);

			this.sentry = {
				captureException,
				captureMessage,
				setUser,
				setContext,
			};

			this.sentryModule = SentryModule;
			this.metrics = this._getMetrics(SentryModule);

			if (this.metrics) {
				console.debug("Sentry metrics API initialized");
			} else {
				console.warn(
					"Sentry metrics API not available (requires SDK 10.25.0+)",
				);
			}

			this.initialized = true;

			this._setInitialMetadata(SentryModule);
			this._setupRouteTracking();

			console.info("Sentry initialized");
			return true;
		} catch (error) {
			console.warn(
				"Failed to load or initialize @sentry/vue package:",
				error,
			);
			return false;
		}
	}

	captureException(
		error: Error | string,
		context?: Record<string, unknown>,
	): void {
		if (!this.initialized || !this.sentry) {
			return;
		}

		try {
			const runtimeContext: RuntimeContext = {
				url: window.location.href,
				userAgent: navigator.userAgent,
			};

			if (error instanceof Error) {
				this.sentry.captureException(error, {
					tags: {
						platform: "frontend",
						component: "frontend",
						layer: "client",
						...(context?.tags as Record<string, string>),
					},
					extra: {
						...(context as Record<string, unknown>),
						url: window.location.href,
						timestamp: new Date().toISOString(),
					},
					contexts: {
						runtime: runtimeContext,
						component: {
							type: "frontend",
							platform: "frontend",
							layer: "client",
							...(context?.source && { source: context.source }),
						},
						...((context?.contexts as Record<string, unknown>) ||
							({} as Record<string, unknown>)),
					},
				} as Parameters<typeof this.sentry.captureException>[1]);
			} else {
				this.sentry.captureMessage(error, {
					level: "error",
					extra: {
						...(context as Record<string, unknown>),
						url: window.location.href,
						timestamp: new Date().toISOString(),
					},
					contexts: {
						runtime: runtimeContext,
						...((context?.contexts as Record<string, unknown>) ||
							({} as Record<string, unknown>)),
					},
				} as Parameters<typeof this.sentry.captureMessage>[1]);
			}
		} catch (e) {
			console.warn("Failed to capture exception:", e);
		}
	}

	captureMessage(
		message: string,
		level: "info" | "warning" | "error" = "info",
		context?: Record<string, unknown>,
	): void {
		if (!this.initialized || !this.sentry) {
			return;
		}

		try {
			this.sentry.captureMessage(message, {
				level,
				tags: {
					platform: "frontend",
					component: "frontend",
					layer: "client",
					...(context?.tags as Record<string, string>),
				},
				extra: {
					...(context as Record<string, unknown>),
					url: window.location.href,
					timestamp: new Date().toISOString(),
				},
				contexts: {
					runtime: {
						url: window.location.href,
						userAgent: navigator.userAgent,
					} as RuntimeContext,
					component: {
						type: "frontend",
						platform: "frontend",
						layer: "client",
					},
					...((context?.contexts as Record<string, unknown>) ||
						({} as Record<string, unknown>)),
				},
			} as Parameters<typeof this.sentry.captureMessage>[1]);
		} catch (e) {
			console.warn("Failed to capture message:", e);
		}
	}

	setUser(user: {
		id?: string;
		email?: string;
		username?: string;
		[key: string]: unknown;
	}): void {
		if (!this.initialized || !this.sentry) {
			return;
		}

		try {
			const { setUser } = this.sentry;
			setUser(user);
		} catch (e) {
			console.warn("Failed to set user in Sentry:", e);
		}
	}

	setContext(key: string, value: unknown): void {
		if (!this.initialized || !this.sentry) {
			return;
		}

		try {
			const { setContext } = this.sentry;
			// Sentry's setContext expects an object with string keys
			if (
				value !== null &&
				typeof value === "object" &&
				!Array.isArray(value)
			) {
				setContext(key, value as Record<string, unknown>);
			} else {
				// If value is not an object, wrap it in an object
				setContext(key, { value });
			}
		} catch (e) {
			console.warn("Failed to set context in Sentry:", e);
		}
	}

	private _setInitialMetadata(SentryModule: SentryModule): void {
		if (!this.initialized || !SentryModule) {
			return;
		}

		try {
			if (SentryModule.setTag) {
				SentryModule.setTag("platform", "frontend");
				SentryModule.setTag("component", "frontend");
				SentryModule.setTag("layer", "client");
				SentryModule.setTag("framework", "writer-framework");

				const appMetadata = this._getAppMetadata();
				if (appMetadata.agent_id) {
					SentryModule.setTag("agent_id", appMetadata.agent_id);
				}
				if (appMetadata.organization_id) {
					SentryModule.setTag(
						"organization_id",
						appMetadata.organization_id,
					);
				}
				if (appMetadata.mode) {
					SentryModule.setTag("mode", appMetadata.mode);
				}
			}

			if (SentryModule.setContext) {
				const appMetadata = this._getAppMetadata();
				SentryModule.setContext("application", appMetadata);
				SentryModule.setContext("runtime", {
					name: "browser",
					user_agent: navigator.userAgent,
					language: navigator.language,
				});
				SentryModule.setContext("component", {
					type: "frontend",
					platform: "frontend",
					layer: "client",
				});
			}
		} catch (e) {
			console.warn("Failed to set initial Sentry metadata:", e);
		}
	}

	private _getMetrics(module: SentryModule): SentryMetrics | null {
		// Try module first
		if (module.metrics) {
			return module.metrics as SentryMetrics;
		}

		// Try global Sentry object (after init)
		if (typeof window !== "undefined") {
			const sentryGlobal = (
				window as { Sentry?: { metrics?: SentryMetrics } }
			).Sentry;
			if (sentryGlobal?.metrics) {
				return sentryGlobal.metrics;
			}
		}

		return null;
	}

	private _setupRouteTracking(): void {
		if (!this.initialized || !this.router) {
			return;
		}

		try {
			const router = this.router as {
				afterEach?: (
					callback: (to: { path: string; name?: string }) => void,
				) => void;
			};

			if (typeof router.afterEach === "function") {
				router.afterEach((to) => {
					let normalizedRoute: string;
					if (to.name) {
						normalizedRoute = to.name;
					} else if (to.path) {
						try {
							const parsedHash = getParsedHash(
								typeof window !== "undefined"
									? window.location.hash
									: "",
							);
							normalizedRoute =
								parsedHash.pageKey || to.path || "unknown";
						} catch {
							normalizedRoute = to.path;
						}
					} else {
						normalizedRoute = "unknown";
					}

					trackRouteChange(normalizedRoute);
				});
			}
		} catch (e) {
			console.warn("Failed to set up Vue Router tracking:", e);
		}
	}

	private _getAppMetadata(): AppMetadata {
		const metadata: AppMetadata = {};

		try {
			if (
				this.app &&
				typeof this.app === "object" &&
				"config" in this.app
			) {
				const vueApp = this.app as {
					config?: {
						globalProperties?: {
							$core?: {
								writerAppId?: { value?: string };
								writerOrgId?: { value?: number | string };
								mode?: { value?: string };
							};
						};
					};
				};

				const core = vueApp?.config?.globalProperties?.$core;
				if (core) {
					if (core.writerAppId?.value) {
						metadata.agent_id = core.writerAppId.value;
					}
					if (core.writerOrgId?.value) {
						metadata.organization_id = String(
							core.writerOrgId.value,
						);
					}
					if (core.mode?.value) {
						metadata.mode = core.mode.value;
					}
				}
			}

			if (!metadata.agent_id && typeof window !== "undefined") {
				const globalCore = (
					window as unknown as {
						core?: { writerAppId?: { value?: string } };
					}
				).core;
				if (globalCore?.writerAppId?.value) {
					metadata.agent_id = globalCore.writerAppId.value;
				}
			}
		} catch (e) {
			console.debug("Failed to get app metadata:", e);
		}

		return metadata;
	}

	private _getMetricsInstance(): SentryMetrics | null {
		if (this.metrics) {
			return this.metrics;
		}
		if (this.sentryModule) {
			return this._getMetrics(this.sentryModule);
		}
		return null;
	}

	private _buildAttributes(
		tags?: Record<string, string>,
	): Record<string, string> {
		const metadata = this._getAppMetadata();
		return {
			...(tags || {}),
			...(metadata.agent_id && { agent_id: metadata.agent_id }),
			...(metadata.organization_id && {
				organization_id: metadata.organization_id,
			}),
			...(metadata.mode && { mode: metadata.mode }),
		};
	}

	incrementMetric(
		name: string,
		options?: SentryIncrementMetricOptions,
	): void {
		if (!this.initialized) {
			return;
		}

		const metrics = this._getMetricsInstance();
		if (!metrics) {
			return;
		}

		try {
			metrics.count(name, options?.value ?? 1, {
				attributes: this._buildAttributes(options?.tags),
				unit: options?.unit,
			});
		} catch (e) {
			console.warn(`Failed to send metric ${name}:`, e);
		}
	}

	recordDistribution(
		name: string,
		value: number,
		options?: SentryMetricOptions,
	): void {
		if (!this.initialized) {
			return;
		}

		const metrics = this._getMetricsInstance();
		if (!metrics) {
			return;
		}

		try {
			metrics.distribution(name, value, {
				attributes: this._buildAttributes(options?.tags),
				unit: options?.unit,
			});
		} catch (e) {
			console.warn(`Failed to send distribution ${name}:`, e);
		}
	}

	setGauge(name: string, value: number, options?: SentryMetricOptions): void {
		if (!this.initialized) {
			return;
		}

		const metrics = this._getMetricsInstance();
		if (!metrics) {
			return;
		}

		try {
			metrics.gauge(name, value, {
				attributes: this._buildAttributes(options?.tags),
				unit: options?.unit,
			});
		} catch (e) {
			console.warn(`Failed to send gauge ${name}:`, e);
		}
	}
}
