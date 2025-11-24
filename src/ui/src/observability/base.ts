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
			// eslint-disable-next-line no-console
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
		if (name === null || name === undefined) {
			const envProvider = import.meta.env.VITE_OBSERVABILITY_PROVIDER;
			if (envProvider) {
				name = envProvider;
			} else {
				for (const [
					providerName,
					provider,
				] of this.providers.entries()) {
					if (provider.isEnabled()) {
						name = providerName;
						break;
					}
				}
			}
		}

		if (!name) {
			// eslint-disable-next-line no-console
			console.info("No observability provider configured");
			return false;
		}

		const provider = this.getProvider(name);
		if (!provider) {
			// eslint-disable-next-line no-console
			console.warn(
				`Observability provider '${name}' not found. Available: ${this.listProviders().join(", ")}`,
			);
			return false;
		}

		if (!provider.isEnabled()) {
			// eslint-disable-next-line no-console
			console.info(`Observability provider '${name}' is disabled`);
			return false;
		}

		try {
			const result = provider.initialize(app, router);
			if (result instanceof Promise) {
				return result
					.then((success) => {
						if (success) {
							this.initializedProvider = provider;
							// eslint-disable-next-line no-console
							console.info(
								`Initialized observability provider: ${name}`,
							);
							return true;
						} else {
							// eslint-disable-next-line no-console
							console.warn(
								`Failed to initialize observability provider: ${name}`,
							);
							return false;
						}
					})
					.catch((error) => {
						// eslint-disable-next-line no-console
						console.error(
							`Error initializing observability provider '${name}':`,
							error,
						);
						return false;
					});
			} else {
				if (result) {
					this.initializedProvider = provider;
					// eslint-disable-next-line no-console
					console.info(`Initialized observability provider: ${name}`);
					return true;
				} else {
					// eslint-disable-next-line no-console
					console.warn(
						`Failed to initialize observability provider: ${name}`,
					);
					return false;
				}
			}
		} catch (error) {
			// eslint-disable-next-line no-console
			console.error(
				`Error initializing observability provider '${name}':`,
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
