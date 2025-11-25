import { useLogger } from "./useLogger.js";
import { useWriterApi } from "./useWriterApi.js";
import type { Core } from "@/writerTypes";

export function useConfigJs(wf: Core) {
	const logger = useLogger();

	async function loadConfigJs(): Promise<void> {
		if (wf.isWriterCloudApp.value) {
			logger.log("Skipping config.js load - not a Writer Cloud App");
			return;
		}

		if (
			typeof window !== "undefined" &&
			(window as { __WRITER_APP_CONFIG__?: unknown })
				.__WRITER_APP_CONFIG__
		) {
			return;
		}

		try {
			const { writerApi } = useWriterApi();
			const configJsContent = await writerApi.fetchConfigJs();

			const script = document.createElement("script");
			script.textContent = configJsContent;
			document.head.appendChild(script);
		} catch (err) {
			logger.warn("Failed to load config.js via WriterApi ", err);
		}
	}

	return {
		loadConfigJs,
	};
}
