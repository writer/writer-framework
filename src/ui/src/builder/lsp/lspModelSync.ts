/**
 * Manual LSP Document Synchronization Helper
 *
 * This module provides manual textDocument/didOpen and textDocument/didChange
 * synchronization for Monaco Editor models with the LSP client.
 *
 * Required when using Monaco Editor in a browser environment (no filesystem)
 * where automatic document sync may not work properly.
 *
 * Based on: https://peerprep.dev/tech-blog/lsp
 */

import type * as monaco from "monaco-editor";
import { useLogger } from "../../composables/useLogger.js";
import { getLSPClient } from "./lspClientRegistry.js";

const logger = useLogger();

/**
 * Manually synchronizes a Monaco model with the LSP server.
 * Sends textDocument/didOpen when the model is created and
 * textDocument/didChange when the content changes.
 *
 * Content change notifications are debounced (300ms) to avoid flooding
 * the LSP server with notifications on every keystroke.
 *
 * @param model - The Monaco editor model to synchronize
 * @returns Disposable to stop synchronization
 */
export function syncModelWithLSP(
	model: monaco.editor.ITextModel,
): monaco.IDisposable {
	const lspClient = getLSPClient();
	if (!lspClient) {
		return { dispose: () => {} };
	}

	const uri = model.uri.toString();
	const languageId = model.getLanguageId();

	let timeoutId: ReturnType<typeof setTimeout> | null = null;
	let debounceTimeoutId: ReturnType<typeof setTimeout> | null = null;

	// Wait a bit for the LSP client to be fully ready
	timeoutId = setTimeout(() => {
		timeoutId = null;
		// Send textDocument/didOpen
		lspClient
			.sendNotification("textDocument/didOpen", {
				textDocument: {
					uri,
					languageId,
					version: model.getVersionId(),
					text: model.getValue(),
				},
			})
			.catch((error: unknown) => {
				logger.error("Failed to send textDocument/didOpen:", error);
			});
	}, 100);

	// Listen for content changes and send textDocument/didChange (debounced)
	const changeDisposable = model.onDidChangeContent(() => {
		// Clear any pending debounced notification
		if (debounceTimeoutId !== null) {
			clearTimeout(debounceTimeoutId);
		}

		// Schedule a new notification after 300ms of inactivity
		debounceTimeoutId = setTimeout(() => {
			debounceTimeoutId = null;
			lspClient
				.sendNotification("textDocument/didChange", {
					textDocument: {
						uri,
						version: model.getVersionId(),
					},
					contentChanges: [
						{
							text: model.getValue(),
						},
					],
				})
				.catch((error: unknown) => {
					logger.error(
						"Failed to send textDocument/didChange:",
						error,
					);
				});
		}, 300);
	});

	// Return disposable that sends textDocument/didClose and stops listening
	return {
		dispose: () => {
			// Clear pending timeout to prevent didOpen after didClose
			if (timeoutId !== null) {
				clearTimeout(timeoutId);
				timeoutId = null;
			}

			// Clear pending debounced change notification
			if (debounceTimeoutId !== null) {
				clearTimeout(debounceTimeoutId);
				debounceTimeoutId = null;
			}

			changeDisposable.dispose();
			lspClient
				.sendNotification("textDocument/didClose", {
					textDocument: { uri },
				})
				.catch((error: unknown) => {
					logger.error(
						"Failed to send textDocument/didClose:",
						error,
					);
				});
		},
	};
}
