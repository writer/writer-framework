import { useLogger } from "./useLogger.js";
import { useWriterApi } from "./useWriterApi.js";
import type { Core } from "@/writerTypes";

export function useConfigJs(wf: Core) {
	const logger = useLogger();

	async function loadConfigJs(): Promise<void> {
		logger.log(
			`loadConfigJs called. isWriterCloudApp: ${wf.isWriterCloudApp.value}, writerAppId: ${wf.writerAppId.value}, writerOrgId: ${wf.writerOrgId.value}`,
		);

		if (wf.isWriterCloudApp.value) {
			logger.log("Skipping config.js load - not a Writer Cloud App");
			return;
		}

		if (
			typeof window !== "undefined" &&
			(window as { __WRITER_APP_CONFIG__?: unknown })
				.__WRITER_APP_CONFIG__
		) {
			logger.log("config.js already loaded");
			return;
		}

		try {
			const { writerApi } = useWriterApi();
			const configJsContent = await writerApi.fetchConfigJs();

			const script = document.createElement("script");
			script.textContent = configJsContent;
			document.head.appendChild(script);
			logger.log("config.js loaded successfully via WriterApi");
		} catch (error) {
			logger.warn(
				"Failed to load config.js via WriterApi (this is expected if the file doesn't exist)",
				error,
			);
		}
	}

	return {
		loadConfigJs,
	};
}
