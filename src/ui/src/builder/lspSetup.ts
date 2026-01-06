/**
 * LSP Setup and Initialization
 *
 * Handles all VSCode services and LSP client initialization for Python language support.
 */

import { initialize as initializeVSCodeServices } from "@codingame/monaco-vscode-api/services";
import { initializeLSPClient } from "./lspClient.js";
import { registerLSPCompletionProvider } from "./lspCompletionProvider.js";
import { useLogger } from "../composables/useLogger.js";

const logger = useLogger();

let vscodeServicesReady = false;

/**
 * Initialize VSCode services required for LSP.
 * This sets up the minimal services needed for monaco-vscode-api integration.
 *
 * @returns Promise that resolves to true if successful
 */
async function initializeVSCodeServicesForLSP(): Promise<boolean> {
	if (vscodeServicesReady) return true;

	try {
		// Import required service overrides for LSP support
		const getTextMateServiceOverride = (
			await import("@codingame/monaco-vscode-textmate-service-override")
		).default;
		const getThemeServiceOverride = (
			await import("@codingame/monaco-vscode-theme-service-override")
		).default;
		const getLanguagesServiceOverride = (
			await import("@codingame/monaco-vscode-languages-service-override")
		).default;

		// Initialize with minimal services
		await initializeVSCodeServices({
			...getTextMateServiceOverride(),
			...getThemeServiceOverride(),
			...getLanguagesServiceOverride(),
		});

		vscodeServicesReady = true;
		return true;
	} catch (error) {
		logger.warn("VSCode services initialization failed:", error);
		return false;
	}
}

/**
 * Complete LSP setup: Initialize VSCode services, LSP client, and completion provider.
 * This is the main entry point for setting up Python language support.
 *
 * @returns Promise that resolves to true if setup was successful
 */
export async function setupLSP(): Promise<boolean> {
	try {
		// Step 1: Initialize VSCode services
		const servicesReady = await initializeVSCodeServicesForLSP();
		if (!servicesReady) {
			return false;
		}

		// Step 2: Wait for DOM to be fully ready
		await new Promise((resolve) => setTimeout(resolve, 100));

		// Step 3: Initialize LSP client
		const lspInitialized = await initializeLSPClient();
		if (!lspInitialized) {
			return false;
		}

		// Step 4: Register completion provider
		const monaco = await import("monaco-editor");
		registerLSPCompletionProvider(monaco);

		logger.log("Python LSP client ready");
		return true;
	} catch (error) {
		logger.error("Failed to setup LSP:", error);
		return false;
	}
}
