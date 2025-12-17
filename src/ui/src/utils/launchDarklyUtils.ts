export type LaunchDarklyEnvironment = "Development" | "Production" | "Test";

const LAUNCHDARKLY_ENV_DEVELOPMENT: LaunchDarklyEnvironment = "Development";
const LAUNCHDARKLY_ENV_PRODUCTION: LaunchDarklyEnvironment = "Production";
const LAUNCHDARKLY_ENV_TEST: LaunchDarklyEnvironment = "Test";
const LAUNCHDARKLY_ENV_DEFAULT: LaunchDarklyEnvironment =
	LAUNCHDARKLY_ENV_DEVELOPMENT;

export function getLaunchDarklyClientId(): string | undefined {
	if (typeof window !== "undefined") {
		const config = window.__WRITER_APP_CONFIG__;
		return config?.LAUNCH_DARKLY;
	}

	return undefined;
}

export function getLaunchDarklyEnvironment(): LaunchDarklyEnvironment {
	const viteMode = import.meta.env.MODE;
	if (viteMode) {
		if (["development", "dev"].includes(viteMode)) {
			return LAUNCHDARKLY_ENV_DEVELOPMENT;
		}
		if (["production", "prod"].includes(viteMode)) {
			return LAUNCHDARKLY_ENV_PRODUCTION;
		}
		if (viteMode === "test") {
			return LAUNCHDARKLY_ENV_TEST;
		}
	}

	return LAUNCHDARKLY_ENV_DEFAULT;
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
function safeFlagEvaluation<T>(
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
		if (typeof override === typeof defaultValue) {
			if (logOverride) {
				console.debug(
					`Using override for flag '${flagKey}':`,
					override,
				);
			}
			return override as T;
		} else {
			console.warn(
				`Flag override type mismatch for '${flagKey}': expected ${typeof defaultValue}, got ${typeof override}`,
			);
		}
	}

	return safeFlagEvaluation(flagKey, evaluationFunc, defaultValue);
}
/* eslint-enable no-console */
