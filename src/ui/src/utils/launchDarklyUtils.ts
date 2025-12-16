export type LaunchDarklyEnvironment = "Development" | "Production" | "Test";

export const LAUNCHDARKLY_ENV_DEVELOPMENT: LaunchDarklyEnvironment =
	"Development";
export const LAUNCHDARKLY_ENV_PRODUCTION: LaunchDarklyEnvironment =
	"Production";
export const LAUNCHDARKLY_ENV_TEST: LaunchDarklyEnvironment = "Test";

export const LAUNCHDARKLY_ENVIRONMENTS: readonly LaunchDarklyEnvironment[] = [
	LAUNCHDARKLY_ENV_DEVELOPMENT,
	LAUNCHDARKLY_ENV_PRODUCTION,
	LAUNCHDARKLY_ENV_TEST,
] as const;

export const LAUNCHDARKLY_ENV_DEFAULT: LaunchDarklyEnvironment =
	LAUNCHDARKLY_ENV_DEVELOPMENT;

interface WriterAppConfig {
	launchDarklyClientId?: string;
	launchDarklyEnvironment?: string;
}

interface WindowWithConfig extends Window {
	__WRITER_APP_CONFIG__?: WriterAppConfig;
}

export function getLaunchDarklyClientId(): string | undefined {
	if (typeof window !== "undefined") {
		const config = (window as WindowWithConfig).__WRITER_APP_CONFIG__;
		if (config?.launchDarklyClientId) {
			return config.launchDarklyClientId;
		}
	}

	return undefined;
}

export function getLaunchDarklyEnvironment(): LaunchDarklyEnvironment {
	if (typeof window !== "undefined") {
		const config = (window as WindowWithConfig).__WRITER_APP_CONFIG__;
		if (config?.launchDarklyEnvironment) {
			const env = config.launchDarklyEnvironment;
			if (
				env === LAUNCHDARKLY_ENV_DEVELOPMENT ||
				env === LAUNCHDARKLY_ENV_PRODUCTION ||
				env === LAUNCHDARKLY_ENV_TEST
			) {
				return env;
			}
		}
	}

	const viteMode = import.meta.env.MODE;
	if (viteMode) {
		if (viteMode === "development" || viteMode === "dev") {
			return LAUNCHDARKLY_ENV_DEVELOPMENT;
		}
		if (viteMode === "production" || viteMode === "prod") {
			return LAUNCHDARKLY_ENV_PRODUCTION;
		}
		if (viteMode === "test") {
			return LAUNCHDARKLY_ENV_TEST;
		}
	}

	return LAUNCHDARKLY_ENV_DEFAULT;
}

export function isLaunchDarklyEnabled(): boolean {
	return getLaunchDarklyClientId() !== undefined;
}

function getFlagOverride(
	flagKey: string,
	overrideSource?: string,
): boolean | string | undefined {
	const source = overrideSource ?? "localStorage";

	if (source === "localStorage" && typeof window !== "undefined") {
		try {
			const envKey = flagKey.toUpperCase().replace(/[-.]/g, "_");
			const overrideKey = `LAUNCHDARKLY_FLAG_OVERRIDE_${envKey}`;
			const overrideValue = localStorage.getItem(overrideKey);

			if (overrideValue !== null) {
				const overrideLower = overrideValue.toLowerCase().trim();
				if (
					overrideLower === "true" ||
					overrideLower === "1" ||
					overrideLower === "yes" ||
					overrideLower === "on"
				) {
					return true;
				}
				if (
					overrideLower === "false" ||
					overrideLower === "0" ||
					overrideLower === "no" ||
					overrideLower === "off"
				) {
					return false;
				}
				return overrideValue;
			}
		} catch {
			// localStorage may not be available
		}
	}

	return undefined;
}

/* eslint-disable no-console */
export function safeFlagEvaluation<T>(
	flagKey: string,
	evaluationFunc: () => T,
	defaultValue: T,
	logErrors = true,
): T {
	try {
		return evaluationFunc();
	} catch (error) {
		if (logErrors) {
			console.warn(
				`Feature flag evaluation failed for '${flagKey}':`,
				error,
			);
		}
		return defaultValue;
	}
}

export function evaluateFlagWithOverride<T>(
	flagKey: string,
	evaluationFunc: () => T,
	defaultValue: T,
	logOverride = true,
): T {
	const override = getFlagOverride(flagKey);
	if (override !== undefined) {
		if (logOverride) {
			console.debug(`Using override for flag '${flagKey}':`, override);
		}
		return override as T;
	}

	return safeFlagEvaluation(flagKey, evaluationFunc, defaultValue);
}
/* eslint-enable no-console */

