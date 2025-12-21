import { useLogger } from "./useLogger.js";
import { useWriterApi } from "./useWriterApi.js";
import type { ObservableCore } from "./useObservabilityMetric.js";
import type { WriterAppConfig } from "@/writerTypes";

function decodeConfig(appConfigRaw: WriterAppConfig | string): WriterAppConfig {
	if (typeof appConfigRaw === "string") {
		try {
			return JSON.parse(atob(appConfigRaw));
		} catch (err) {
			throw new Error(`Failed to decode config: ${err}`);
		}
	}

	return appConfigRaw;
}

export function useConfigJs(wf: ObservableCore) {
	const logger = useLogger();

	async function loadConfigJs(): Promise<void> {
		if (typeof window !== "undefined" && window.__WRITER_APP_CONFIG__) {
			const rawConfig = window.__WRITER_APP_CONFIG__;
			if (typeof rawConfig === "string") {
				try {
					window.__WRITER_APP_CONFIG__ = decodeConfig(rawConfig);
				} catch (err) {
					logger.error("Failed to decode __WRITER_APP_CONFIG__", err);
				}
			}
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

		if (window.__WRITER_APP_CONFIG__) {
			const rawConfig = window.__WRITER_APP_CONFIG__;
			if (typeof rawConfig === "string") {
				try {
					window.__WRITER_APP_CONFIG__ = decodeConfig(rawConfig);
				} catch (err) {
					logger.error("Failed to decode __WRITER_APP_CONFIG__", err);
				}
			}
		}
	}

	return {
		loadConfigJs,
	};
}
