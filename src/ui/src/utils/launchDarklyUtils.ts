export type LaunchDarklyEnvironment = "Development" | "Production" | "Test";

const DEFAULT_ENVIRONMENT: LaunchDarklyEnvironment = "Development";

export function getLaunchDarklyClientId(): string | undefined {
	return typeof window !== "undefined"
		? window.__WRITER_APP_CONFIG__?.LAUNCH_DARKLY
		: undefined;
}

export function getLaunchDarklyEnvironment(): LaunchDarklyEnvironment {
	const viteMode = import.meta.env.MODE;
	if (viteMode) {
		if (["development", "dev"].includes(viteMode)) {
			return "Development";
		}
		if (["production", "prod"].includes(viteMode)) {
			return "Production";
		}
		if (viteMode === "test") {
			return "Test";
		}
	}

	return DEFAULT_ENVIRONMENT;
}

function getFlagOverride(flagKey: string): boolean | string | undefined {
	if (typeof window === "undefined") {
		return undefined;
	}

	const envKey = flagKey.toUpperCase().replace(/[-.]/g, "_");
	const overrideKey = `LAUNCHDARKLY_FLAG_OVERRIDE_${envKey}`;
	const overrideValue = localStorage.getItem(overrideKey);

	if (!overrideValue) {
		return undefined;
	}

	const overrideLower = overrideValue.toLowerCase().trim();
	if (["true", "1", "yes", "on"].includes(overrideLower)) {
		return true;
	}
	if (["false", "0", "no", "off"].includes(overrideLower)) {
		return false;
	}
	return overrideValue;
}

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
