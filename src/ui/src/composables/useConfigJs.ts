import { useLogger } from "./useLogger.js";
import { useWriterApi } from "./useWriterApi.js";
import type { ObservableCore } from "./useObservabilityMetric.js";

export function useConfigJs(wf: ObservableCore) {
	const logger = useLogger();

	async function loadConfigJs(): Promise<void> {
		if (typeof window !== "undefined" && window.__WRITER_APP_CONFIG__) {
			return;
		}

		const { writerApi } = useWriterApi();
		const configJsContent = await writerApi.fetchConfigJs();

		if (!configJsContent) {
			if (wf.isWriterCloudApp.value) {
				logger.warn("Failed to load config.js via WriterApi");
			} else {
				logger.log("config.js not available (not a Writer Cloud App)");
			}
			return;
		}

		const script = document.createElement("script");
		script.textContent = configJsContent;
		document.head.appendChild(script);
	}

	return {
		loadConfigJs,
	};
}
