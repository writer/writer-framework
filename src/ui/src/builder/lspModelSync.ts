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
import { useLogger } from "../composables/useLogger.js";
import { getLSPClient } from "./lspClient.js";

const logger = useLogger();

/**
 * Manually synchronizes a Monaco model with the LSP server.
 * Sends textDocument/didOpen when the model is created and
 * textDocument/didChange when the content changes.
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

	// Wait a bit for the LSP client to be fully ready
	setTimeout(() => {
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

	// Listen for content changes and send textDocument/didChange
	const changeDisposable = model.onDidChangeContent(() => {
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
				logger.error("Failed to send textDocument/didChange:", error);
			});
	});

	// Return disposable that sends textDocument/didClose and stops listening
	return {
		dispose: () => {
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
