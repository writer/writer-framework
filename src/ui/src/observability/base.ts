import { useLogger } from "@/composables/useLogger";

const logger = useLogger();

export interface ObservabilityProvider {
	initialize(app?: unknown, router?: unknown): boolean | Promise<boolean>;
	captureException(
		error: Error | string,
		context?: Record<string, unknown>,
	): void;
	captureMessage(
		message: string,
		level?: "info" | "warning" | "error",
		context?: Record<string, unknown>,
	): void;
	setUser(user: {
		id?: string;
		email?: string;
		username?: string;
		[key: string]: unknown;
	}): void;
	setContext(key: string, value: unknown): void;
	isEnabled(): boolean;
	getName(): string;
	incrementMetric?(name: string, options?: IncrementMetricOptions): void;
	recordDistribution?(
		name: string,
		value: number,
		options?: RecordDistributionOptions,
	): void;
	setGauge?(
		name: string,
		value: number,
		options?: RecordDistributionOptions,
	): void;
}

export interface IncrementMetricOptions {
	tags?: Record<string, string>;
	unit?: string;
	value?: number;
}

export interface RecordDistributionOptions {
	tags?: Record<string, string>;
	unit?: string;
}

export class ObservabilityRegistry {
	private providers: Map<string, ObservabilityProvider> = new Map();
	private initializedProvider: ObservabilityProvider | null = null;

	register(name: string, provider: ObservabilityProvider): void {
		if (this.providers.has(name)) {
			logger.warn(`Overwriting existing provider '${name}'`);
		}

		this.providers.set(name, provider);
	}

	getProvider(name: string): ObservabilityProvider | null {
		return this.providers.get(name) || null;
	}

	listProviders(): string[] {
		return Array.from(this.providers.keys());
	}

	async initializeProvider(
		name?: string | null,
		app?: unknown,
		router?: unknown,
	): Promise<boolean> {
		let providerName: string | null | undefined = name;

		if (providerName === null || providerName === undefined) {
			const envProvider = import.meta.env.VITE_OBSERVABILITY_PROVIDER;
			if (envProvider) {
				providerName = envProvider;
			} else {
				for (const [
					enabledProviderName,
					provider,
				] of this.providers.entries()) {
					if (provider.isEnabled()) {
						providerName = enabledProviderName;
						break;
					}
				}
			}
		}

		if (!providerName) {
			logger.info("No observability provider configured");
			return false;
		}

		const provider = this.getProvider(providerName);
		if (!provider) {
			logger.warn(
				`Observability provider '${providerName}' not found. Available: ${this.listProviders().join(", ")}`,
			);
			return false;
		}

		if (!provider.isEnabled()) {
			logger.warn(
				`Observability provider '${providerName}' is disabled. Check if LaunchDarkly client ID is configured.`,
			);
			return false;
		}

		try {
			const result = provider.initialize(app, router);
			if (result instanceof Promise) {
				return result
					.then((success) => {
						if (success) {
							this.initializedProvider = provider;
							logger.info(
								`[LaunchDarkly] Initialized observability provider: ${providerName}`,
							);
							return true;
						} else {
							logger.warn(
								`[LaunchDarkly] Failed to initialize observability provider: ${providerName}`,
							);
							return false;
						}
					})
					.catch((error) => {
						logger.error(
							`[LaunchDarkly] Error initializing observability provider '${providerName}':`,
							error,
						);
						return false;
					});
			} else {
				if (result) {
					this.initializedProvider = provider;
					logger.info(
						`[LaunchDarkly] Initialized observability provider: ${providerName}`,
					);
					return true;
				} else {
					logger.warn(
						`[LaunchDarkly] Failed to initialize observability provider: ${providerName}`,
					);
					return false;
				}
			}
		} catch (error) {
			logger.error(
				`[LaunchDarkly] Error initializing observability provider '${providerName}':`,
				error,
			);
			return false;
		}
	}

	getInitializedProvider(): ObservabilityProvider | null {
		return this.initializedProvider;
	}

	captureException(
		error: Error | string,
		context?: Record<string, unknown>,
	): void {
		if (this.initializedProvider) {
			this.initializedProvider.captureException(error, context);
		}
	}

	captureMessage(
		message: string,
		level?: "info" | "warning" | "error",
		context?: Record<string, unknown>,
	): void {
		if (this.initializedProvider) {
			this.initializedProvider.captureMessage(message, level, context);
		}
	}

	incrementMetric(
		name: string,
		options?: { tags?: Record<string, string>; value?: number },
	): void {
		if (this.initializedProvider?.incrementMetric) {
			this.initializedProvider.incrementMetric(name, options);
		}
	}

	recordDistribution(
		name: string,
		value: number,
		options?: { tags?: Record<string, string>; unit?: string },
	): void {
		if (this.initializedProvider?.recordDistribution) {
			this.initializedProvider.recordDistribution(name, value, options);
		}
	}

	setGauge(
		name: string,
		value: number,
		options?: { tags?: Record<string, string>; unit?: string },
	): void {
		if (this.initializedProvider?.setGauge) {
			this.initializedProvider.setGauge(name, value, options);
		}
	}
}
