import { useLogger } from "./useLogger";
import { useConfigJs } from "./useConfigJs";
import type { Core } from "@/writerTypes";
import { getLaunchDarklyClientId } from "@/utils/launchDarklyUtils";
import {
	buildLDContext,
	initializeLaunchDarkly,
} from "@/core/launchDarklyClient";
import {
	incrementMetric,
	METRIC_NAMES,
	recordDistribution,
} from "@/observability/frontendMetrics";

export function useObservabilityMetric(wf: Core) {
	const logger = useLogger();
	const { loadConfigJs } = useConfigJs(wf);
	let isLaunchDarklyInitialized = false;

	async function initialize(sessionId: string | null): Promise<void> {
		try {
			await loadConfigJs();

			const clientId = getLaunchDarklyClientId();

			if (!clientId) {
				logger.log(
					"LaunchDarkly client ID not available, skipping initialization",
				);
				return;
			}

			if (!sessionId) {
				logger.warn(
					"LaunchDarkly initialization skipped: sessionId not provided",
				);
				return;
			}

			const context = buildLDContext(
				sessionId,
				wf.mode.value,
				wf.writerApplication.value,
			);

			await initializeLaunchDarkly(context, clientId);

			isLaunchDarklyInitialized = true;
		} catch (error) {
			logger.warn("LaunchDarkly initialization failed", error);
		}
	}

	function updateSocketDuration(connectStartTime: number): void {
		if (typeof performance === "undefined") {
			return;
		}

		const connectDuration = performance.now() - connectStartTime;
		recordDistribution(
			METRIC_NAMES.WEBSOCKET_CONNECT_DURATION,
			connectDuration,
			{
				tags: { mode: wf.mode.value || "unknown" },
				unit: "ms",
			},
		);
		incrementMetric(METRIC_NAMES.WEBSOCKET_CONNECTED, {
			tags: { mode: wf.mode.value || "unknown" },
		});
	}

	return {
		initialize,
		updateSocketDuration,
		isLaunchDarklyInitialized: () => isLaunchDarklyInitialized,
	};
}
