/**
 * Manual LSP Completion Provider for Monaco Editor
 *
 * This provider manually bridges Monaco Editor's completion API with the LSP client.
 * This is needed when using monaco-vscode-api if the automatic wiring doesn't work.
 */

import type * as monaco from "monaco-editor";
import { getLSPClient } from "./lspClientRegistry.js";
import { useLogger } from "../../composables/useLogger.js";

type LSPCompletionItem = {
	label: string;
	kind?: number;
	detail?: string;
	documentation?: string;
	insertText?: string;
	insertTextFormat?: number; // 1 = PlainText, 2 = Snippet
	sortText?: string;
	filterText?: string;
	textEdit?: {
		newText: string;
		range: unknown;
	};
};

const logger = useLogger();

/**
 * Common Python snippets to augment LSP completions.
 * These provide useful code templates with tab stops.
 */
/* eslint-disable no-template-curly-in-string */
const PYTHON_SNIPPETS: Record<
	string,
	{
		label: string;
		snippet: string;
		detail: string;
		documentation: string;
	}
> = {
	class: {
		label: "class",
		snippet:
			"class ${1:ClassName}:\n\tdef __init__(self, ${2:args}):\n\t\t${0:pass}",
		detail: "Class definition",
		documentation: "Create a new class with __init__ method",
	},
	def: {
		label: "def",
		snippet: "def ${1:function_name}(${2:args}):\n\t${0:pass}",
		detail: "Function definition",
		documentation: "Create a new function",
	},
	for: {
		label: "for",
		snippet: "for ${1:item} in ${2:iterable}:\n\t${0:pass}",
		detail: "For loop",
		documentation: "Iterate over an iterable",
	},
	while: {
		label: "while",
		snippet: "while ${1:condition}:\n\t${0:pass}",
		detail: "While loop",
		documentation: "Loop while condition is true",
	},
	if: {
		label: "if",
		snippet: "if ${1:condition}:\n\t${0:pass}",
		detail: "If statement",
		documentation: "Conditional statement",
	},
	elif: {
		label: "elif",
		snippet: "elif ${1:condition}:\n\t${0:pass}",
		detail: "Elif statement",
		documentation: "Else-if conditional",
	},
	else: {
		label: "else",
		snippet: "else:\n\t${0:pass}",
		detail: "Else statement",
		documentation: "Else clause",
	},
	try: {
		label: "try",
		snippet:
			"try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${0:pass}",
		detail: "Try-except block",
		documentation: "Exception handling",
	},
	with: {
		label: "with",
		snippet: "with ${1:expression} as ${2:variable}:\n\t${0:pass}",
		detail: "With statement",
		documentation: "Context manager",
	},
	main: {
		label: "if __name__ == '__main__'",
		snippet: 'if __name__ == "__main__":\n\t${0:pass}',
		detail: "Main guard",
		documentation: "Python main entry point",
	},
};
/* eslint-enable no-template-curly-in-string */

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

				const lspSuggestions = items.map((item: unknown) => {
					const completionItem = item as LSPCompletionItem;

					// Use textEdit.newText if available, otherwise insertText or label
					const insertText =
						completionItem.textEdit?.newText ||
						completionItem.insertText ||
						completionItem.label;

					// Check if this is a snippet (insertTextFormat === 2)
					const isSnippet = completionItem.insertTextFormat === 2;

					const insertTextRule = isSnippet
						? monacoInstance.languages.CompletionItemInsertTextRule
								.InsertAsSnippet
						: undefined;

					return {
						label: completionItem.label,
						kind: convertCompletionItemKind(completionItem.kind),
						detail: completionItem.detail,
						documentation: completionItem.documentation,
						insertText: insertText,
						insertTextRules: insertTextRule,
						range: undefined, // Let Monaco handle the range
						sortText: completionItem.sortText,
						filterText: completionItem.filterText,
					};
				});

				// Add custom Python snippets
				const snippetSuggestions = Object.values(PYTHON_SNIPPETS).map(
					(snippet) => {
						const kind =
							monacoInstance.languages.CompletionItemKind.Snippet;
						const insertTextRules =
							monacoInstance.languages
								.CompletionItemInsertTextRule.InsertAsSnippet;
						return {
							label: snippet.label,
							kind: kind,
							detail: snippet.detail,
							documentation: snippet.documentation,
							insertText: snippet.snippet,
							insertTextRules: insertTextRules,
							range: undefined,
							sortText: `_${snippet.label}`, // Sort snippets near the top
						};
					},
				);

				// Combine LSP suggestions with custom snippets
				const allSuggestions = [
					...lspSuggestions,
					...snippetSuggestions,
				];

				return { suggestions: allSuggestions };
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
