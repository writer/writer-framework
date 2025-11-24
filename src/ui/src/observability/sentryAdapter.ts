import type { ObservabilityProvider } from "./base";

export const SENTRY_DSN_ENV = "VITE_SENTRY_DSN";
export const SENTRY_ENABLED_ENV = "VITE_SENTRY_ENABLED";
export const SENTRY_ENVIRONMENT_ENV = "VITE_SENTRY_ENVIRONMENT";
export const SENTRY_TRACES_SAMPLE_RATE_ENV = "VITE_SENTRY_TRACES_SAMPLE_RATE";
export const SENTRY_REPLAY_SAMPLE_RATE_ENV = "VITE_SENTRY_REPLAY_SAMPLE_RATE";

interface SentryApi {
	captureException: (
		error: Error,
		options?: {
			extra?: Record<string, unknown>;
			contexts?: Record<string, unknown>;
		},
	) => void;
	captureMessage: (
		message: string,
		options?: {
			level?: string;
			extra?: Record<string, unknown>;
			contexts?: Record<string, unknown>;
		},
	) => void;
	setUser: (user: {
		id?: string;
		email?: string;
		username?: string;
		[key: string]: unknown;
	}) => void;
	setContext: (key: string, value: unknown) => void;
}

interface SentryMetrics {
	count: (
		name: string,
		value?: number,
		data?: {
			attributes?: Record<string, string>;
			unit?: string;
		},
	) => void;
	distribution: (
		name: string,
		value: number,
		data?: {
			attributes?: Record<string, string>;
			unit?: string;
		},
	) => void;
	gauge: (
		name: string,
		value: number,
		data?: {
			attributes?: Record<string, string>;
			unit?: string;
		},
	) => void;
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
	browserTracingIntegration?: (options?: {
		router?: unknown;
		tracingOrigins?: (string | RegExp)[];
		routeLabel?: "name" | "path";
	}) => unknown;
	BrowserTracing?: new (options?: {
		router?: unknown;
		tracingOrigins?: (string | RegExp)[];
		routeLabel?: "name" | "path";
	}) => unknown;
}

interface SentryInitConfig {
	dsn: string;
	environment: string;
	tracesSampleRate: number;
	replay: {
		sampleRate: number;
	};
	enableMetrics?: boolean;
	app?: unknown;
	integrations?: unknown[];
}

type BrowserTracingFunction = (options?: {
	router?: unknown;
	tracingOrigins?: (string | RegExp)[];
	routeLabel?: "name" | "path";
}) => unknown;
type BrowserTracingClass = new (options?: {
	router?: unknown;
	tracingOrigins?: (string | RegExp)[];
	routeLabel?: "name" | "path";
}) => unknown;
type BrowserTracingIntegration = BrowserTracingFunction | BrowserTracingClass;

export class SentryAdapter implements ObservabilityProvider {
	private initialized = false;
	private sentry: SentryApi | null = null;
	private metrics: SentryMetrics | null = null;
	private sentryModule: SentryModule | null = null;
	private app: unknown = null;
	private router: unknown = null;

	isEnabled(): boolean {
		return import.meta.env[SENTRY_ENABLED_ENV] !== "false";
	}

	getName(): string {
		return "sentry";
	}

	async initialize(app?: unknown, router?: unknown): Promise<boolean> {
		if (this.initialized) {
			return true;
		}

		if (router) {
			this.router = router;
		}

		try {
			const dsn = import.meta.env[SENTRY_DSN_ENV];
			if (!dsn) {
				// eslint-disable-next-line no-console
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
				// eslint-disable-next-line no-console
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
					// eslint-disable-next-line no-console
					console.warn(
						"BrowserTracing not available. Performance monitoring will be limited.",
					);
				}
			}

			const environment =
				import.meta.env[SENTRY_ENVIRONMENT_ENV] ||
				import.meta.env.MODE ||
				"production";
			const tracesSampleRate = parseFloat(
				import.meta.env[SENTRY_TRACES_SAMPLE_RATE_ENV] || "1.0",
			);
			const replaySampleRate = parseFloat(
				import.meta.env[SENTRY_REPLAY_SAMPLE_RATE_ENV] || "0.1",
			);

			const initConfig: SentryInitConfig = {
				dsn,
				environment,
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
				const tracingOptions: {
					router?: unknown;
					tracingOrigins?: (string | RegExp)[];
					routeLabel?: "name" | "path";
				} = {
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
				// eslint-disable-next-line no-console
				console.debug("Sentry metrics API initialized");
			} else {
				// eslint-disable-next-line no-console
				console.warn(
					"Sentry metrics API not available (requires SDK 10.25.0+)",
				);
			}

			this.initialized = true;

			this._setInitialMetadata(SentryModule);
			this._setupRouteTracking();

			// eslint-disable-next-line no-console
			console.info(`Sentry initialized (environment: ${environment})`);
			return true;
		} catch (error) {
			// eslint-disable-next-line no-console
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
			const runtimeContext = {
				url: window.location.href,
				userAgent: navigator.userAgent,
			};

			if (error instanceof Error) {
				this.sentry.captureException(error, {
					extra: {
						...context,
						url: window.location.href,
						timestamp: new Date().toISOString(),
					},
					contexts: {
						runtime: runtimeContext,
						...((context?.contexts as Record<string, unknown>) ||
							{}),
					},
				});
			} else {
				this.sentry.captureMessage(error, {
					level: "error",
					extra: {
						...context,
						url: window.location.href,
						timestamp: new Date().toISOString(),
					},
					contexts: {
						runtime: runtimeContext,
						...((context?.contexts as Record<string, unknown>) ||
							{}),
					},
				});
			}
		} catch (e) {
			// eslint-disable-next-line no-console
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
				extra: {
					...context,
					url: window.location.href,
					timestamp: new Date().toISOString(),
				},
				contexts: {
					runtime: {
						url: window.location.href,
						userAgent: navigator.userAgent,
					},
					...((context?.contexts as Record<string, unknown>) || {}),
				},
			});
		} catch (e) {
			// eslint-disable-next-line no-console
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
			// eslint-disable-next-line no-console
			console.warn("Failed to set user in Sentry:", e);
		}
	}

	setContext(key: string, value: unknown): void {
		if (!this.initialized || !this.sentry) {
			return;
		}

		try {
			const { setContext } = this.sentry;
			setContext(key, value);
		} catch (e) {
			// eslint-disable-next-line no-console
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
			}
		} catch (e) {
			// eslint-disable-next-line no-console
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
					const route = to.name || to.path || "unknown";
					this.incrementMetric("frontend_route_changes_total", {
						tags: { route },
						unit: "none",
					});
				});
			}
		} catch (e) {
			// eslint-disable-next-line no-console
			console.warn("Failed to set up Vue Router tracking:", e);
		}
	}

	private _getAppMetadata(): {
		agent_id?: string;
		organization_id?: string;
		mode?: string;
	} {
		const metadata: {
			agent_id?: string;
			organization_id?: string;
			mode?: string;
		} = {};

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
			// eslint-disable-next-line no-console
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
		options?: {
			tags?: Record<string, string>;
			unit?: string;
			value?: number;
		},
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
			// eslint-disable-next-line no-console
			console.warn(`Failed to send metric ${name}:`, e);
		}
	}

	recordDistribution(
		name: string,
		value: number,
		options?: {
			tags?: Record<string, string>;
			unit?: string;
		},
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
			// eslint-disable-next-line no-console
			console.warn(`Failed to send distribution ${name}:`, e);
		}
	}

	setGauge(
		name: string,
		value: number,
		options?: {
			tags?: Record<string, string>;
			unit?: string;
		},
	): void {
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
			// eslint-disable-next-line no-console
			console.warn(`Failed to send gauge ${name}:`, e);
		}
	}
}
