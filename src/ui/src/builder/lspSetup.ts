/**
 * LSP Setup and Initialization
 *
 * Handles all VSCode services and LSP client initialization for Python language support.
 */

import { initialize as initializeVSCodeServices } from "@codingame/monaco-vscode-api/services";
import { initializeLSPClient, stopLSPClient } from "./lspClient.js";
import { registerLSPCompletionProvider } from "./lspCompletionProvider.js";
import { setupLSPDiagnostics } from "./lspDiagnostics.js";
import { useLogger } from "../composables/useLogger.js";
import type * as monaco from "monaco-editor";

const logger = useLogger();

let vscodeServicesReady = false;
let diagnosticsDisposable: monaco.IDisposable | null = null;
let completionProviderDisposable: monaco.IDisposable | null = null;

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
		// Note: We only import TextMate (syntax highlighting) and Languages (LSP) services
		const getTextMateServiceOverride = (
			await import("@codingame/monaco-vscode-textmate-service-override")
		).default;
		const getLanguagesServiceOverride = (
			await import("@codingame/monaco-vscode-languages-service-override")
		).default;

		// Initialize with minimal services
		await initializeVSCodeServices({
			...getTextMateServiceOverride(),
			...getLanguagesServiceOverride(),
		});

		vscodeServicesReady = true;
		return true;
	} catch (error) {
		logger.error("Failed to initialize services for LSP:", error);
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

		// Step 3: Initialize LSP client (now waits for full initialization)
		const lspInitialized = await initializeLSPClient();
		if (!lspInitialized) {
			return false;
		}

		// Step 4: Register completion provider and diagnostics
		// Client is now fully ready, safe to set up listeners
		const monaco = await import("monaco-editor");
		completionProviderDisposable = registerLSPCompletionProvider(monaco);
		diagnosticsDisposable = setupLSPDiagnostics(monaco);

		logger.log("Python LSP setup complete with diagnostics");
		return true;
	} catch (error) {
		logger.error("Failed to setup LSP:", error);
		return false;
	}
}

/**
 * Cleanup LSP resources.
 */
export function cleanupLSP() {
	if (completionProviderDisposable) {
		completionProviderDisposable.dispose();
		completionProviderDisposable = null;
	}

	if (diagnosticsDisposable) {
		diagnosticsDisposable.dispose();
		diagnosticsDisposable = null;
	}

	stopLSPClient();
}
