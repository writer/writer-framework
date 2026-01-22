/**
 * LSP Client Registry - Lightweight module for accessing the LSP client instance.
 *
 * This module is separate from lspClient.ts to avoid importing heavy dependencies
 * (monaco-languageclient, vscode-languageclient) in modules that only need to
 * access an already-initialized client.
 */

import type { MonacoLanguageClient } from "monaco-languageclient";

let languageClient: MonacoLanguageClient | null = null;

/**
 * Registers the LSP client instance.
 * Called by lspClient.ts after initialization.
 */
export function registerLSPClient(client: MonacoLanguageClient | null): void {
	languageClient = client;
}

export function getLSPClient(): MonacoLanguageClient | null {
	return languageClient;
}

export function isLSPClientAvailable(): boolean {
	return languageClient !== null;
}
