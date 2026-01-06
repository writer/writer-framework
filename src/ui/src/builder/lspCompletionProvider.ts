/**
 * Manual LSP Completion Provider for Monaco Editor
 *
 * This provider manually bridges Monaco Editor's completion API with the LSP client.
 * This is needed when using monaco-vscode-api if the automatic wiring doesn't work.
 */

import type * as monaco from "monaco-editor";
import { getLSPClient } from "./lspClient.js";
import { useLogger } from "../composables/useLogger.js";

const logger = useLogger();

/**
 * Registers a manual completion provider that forwards requests to the LSP client.
 *
 * @param monacoInstance - The Monaco Editor API instance
 * @returns Disposable to unregister the provider
 */
export function registerLSPCompletionProvider(
	monacoInstance: typeof monaco,
): monaco.IDisposable {
	return monacoInstance.languages.registerCompletionItemProvider("python", {
		provideCompletionItems: async (model, position, context) => {
			const lspClient = getLSPClient();
			if (!lspClient) {
				return { suggestions: [] };
			}

			const uri = model.uri.toString();

			try {
				// Send textDocument/completion request to LSP server
				const result: unknown = await lspClient.sendRequest(
					"textDocument/completion",
					{
						textDocument: { uri },
						position: {
							line: position.lineNumber - 1, // Monaco is 1-based, LSP is 0-based
							character: position.column - 1,
						},
						context: {
							triggerKind: context.triggerKind,
							triggerCharacter: context.triggerCharacter,
						},
					},
				);

				// Convert LSP completion items to Monaco completion items
				const items = Array.isArray(result)
					? result
					: (result as { items?: unknown[] })?.items || [];

				const suggestions = items.map((item: unknown) => {
					const completionItem = item as {
						label: string;
						kind?: number;
						detail?: string;
						documentation?: string;
						insertText?: string;
						sortText?: string;
						filterText?: string;
					};
					return {
						label: completionItem.label,
						kind: convertCompletionItemKind(completionItem.kind),
						detail: completionItem.detail,
						documentation: completionItem.documentation,
						insertText:
							completionItem.insertText || completionItem.label,
						range: undefined, // Let Monaco handle the range
						sortText: completionItem.sortText,
						filterText: completionItem.filterText,
					};
				});

				return { suggestions };
			} catch (error) {
				logger.error("Failed to get LSP completions:", error);
				return { suggestions: [] };
			}
		},
	});
}

/**
 * Converts LSP CompletionItemKind to Monaco CompletionItemKind.
 */
function convertCompletionItemKind(
	lspKind: number | undefined,
): monaco.languages.CompletionItemKind {
	// Import monaco dynamically to avoid circular dependencies
	const monacoInstance = (window as { monaco?: typeof monaco }).monaco;
	if (!monacoInstance) {
		return 0; // Text
	}

	const CompletionItemKind = monacoInstance.languages.CompletionItemKind;

	// LSP CompletionItemKind mapping
	// https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItemKind
	switch (lspKind) {
		case 1:
			return CompletionItemKind.Text;
		case 2:
			return CompletionItemKind.Method;
		case 3:
			return CompletionItemKind.Function;
		case 4:
			return CompletionItemKind.Constructor;
		case 5:
			return CompletionItemKind.Field;
		case 6:
			return CompletionItemKind.Variable;
		case 7:
			return CompletionItemKind.Class;
		case 8:
			return CompletionItemKind.Interface;
		case 9:
			return CompletionItemKind.Module;
		case 10:
			return CompletionItemKind.Property;
		case 11:
			return CompletionItemKind.Unit;
		case 12:
			return CompletionItemKind.Value;
		case 13:
			return CompletionItemKind.Enum;
		case 14:
			return CompletionItemKind.Keyword;
		case 15:
			return CompletionItemKind.Snippet;
		case 16:
			return CompletionItemKind.Color;
		case 17:
			return CompletionItemKind.File;
		case 18:
			return CompletionItemKind.Reference;
		case 19:
			return CompletionItemKind.Folder;
		case 20:
			return CompletionItemKind.EnumMember;
		case 21:
			return CompletionItemKind.Constant;
		case 22:
			return CompletionItemKind.Struct;
		case 23:
			return CompletionItemKind.Event;
		case 24:
			return CompletionItemKind.Operator;
		case 25:
			return CompletionItemKind.TypeParameter;
		default:
			return CompletionItemKind.Text;
	}
}
