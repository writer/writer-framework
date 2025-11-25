/* eslint-disable no-console */
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
}

export class ObservabilityRegistry {
	private providers: Map<string, ObservabilityProvider> = new Map();
	private initializedProvider: ObservabilityProvider | null = null;

	register(name: string, provider: ObservabilityProvider): void {
		if (this.providers.has(name)) {
			console.warn(`Overwriting existing provider '${name}'`);
		}

		this.providers.set(name, provider);
	}

	getProvider(name: string): ObservabilityProvider | null {
		return this.providers.get(name) || null;
	}

	listProviders(): string[] {
		return Array.from(this.providers.keys());
	}

	initializeProvider(
		name?: string | null,
		app?: unknown,
		router?: unknown,
	): boolean | Promise<boolean> {
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
			console.info("No observability provider configured");
			return false;
		}

		const provider = this.getProvider(providerName);
		if (!provider) {
			console.warn(
				`Observability provider '${providerName}' not found. Available: ${this.listProviders().join(", ")}`,
			);
			return false;
		}

		if (!provider.isEnabled()) {
			console.info(
				`Observability provider '${providerName}' is disabled`,
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
							console.info(
								`Initialized observability provider: ${providerName}`,
							);
							return true;
						} else {
							console.warn(
								`Failed to initialize observability provider: ${providerName}`,
							);
							return false;
						}
					})
					.catch((error) => {
						console.error(
							`Error initializing observability provider '${providerName}':`,
							error,
						);
						return false;
					});
			} else {
				if (result) {
					this.initializedProvider = provider;
					console.info(
						`Initialized observability provider: ${providerName}`,
					);
					return true;
				} else {
					console.warn(
						`Failed to initialize observability provider: ${providerName}`,
					);
					return false;
				}
			}
		} catch (error) {
			console.error(
				`Error initializing observability provider '${providerName}':`,
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
}
