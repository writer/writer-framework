import type * as monaco from "monaco-editor";
import { getLSPClient } from "./lspClientRegistry.js";
import { useLogger } from "../../composables/useLogger.js";

const logger = useLogger();

/**
 * Writer framework globals that are available in code blocks and event handlers.
 * These should not be flagged as undefined by the linter.
 */
const WRITER_FRAMEWORK_GLOBALS = new Set([
	// Event handler globals
	"state",
	"payload",
	"context",
	"session",
	"ui",
	"blueprint_runner",
	"vault",
	// Code block globals
	"set_output",
	"result",
	"results",
	"logger",
	// IfElse block globals
	"set_outcome",
]);

/**
 * LSP Diagnostic Severity levels
 */
enum DiagnosticSeverity {
	Error = 1,
	Warning = 2,
	Information = 3,
	Hint = 4,
}

type LSPDiagnostic = {
	uri: string;
	diagnostics: Array<{
		range: {
			start: { line: number; character: number };
			end: { line: number; character: number };
		};
		severity: number;
		message: string;
		source?: string;
		code?: string | number;
	}>;
};

/**
 * Checks if a diagnostic is a false positive for Writer framework globals.
 * Returns true if this diagnostic should be filtered out.
 */
function isWriterFrameworkGlobalError(diagnostic: {
	message: string;
	code?: string | number;
	source?: string;
}): boolean {
	// Check if it's an undefined name error (F821 from pyflakes or flake8)
	if (diagnostic.source === "pyflakes" || diagnostic.source === "flake8") {
		if (
			diagnostic.code === "F821" ||
			diagnostic.message.includes("undefined name")
		) {
			// Extract the variable name from the message
			// Messages are like: "undefined name 'state'" or "F821 undefined name 'state'"
			const match = diagnostic.message.match(/undefined name '([^']+)'/);
			if (match?.[1]) {
				const varName = match[1];
				return WRITER_FRAMEWORK_GLOBALS.has(varName);
			}
		}
	}
	return false;
}

/**
 * Converts LSP diagnostic severity to Monaco marker severity.
 */
function convertSeverity(
	lspSeverity: number,
	monacoInstance: typeof monaco,
): monaco.MarkerSeverity {
	switch (lspSeverity) {
		case DiagnosticSeverity.Error:
			return monacoInstance.MarkerSeverity.Error;
		case DiagnosticSeverity.Warning:
			return monacoInstance.MarkerSeverity.Warning;
		case DiagnosticSeverity.Information:
			return monacoInstance.MarkerSeverity.Info;
		case DiagnosticSeverity.Hint:
			return monacoInstance.MarkerSeverity.Hint;
		default:
			return monacoInstance.MarkerSeverity.Error;
	}
}

/**
 * Sets up a listener for LSP diagnostics and displays them as Monaco markers.
 *
 * @param monacoInstance - The Monaco Editor API instance
 * @returns Disposable to unregister the listener
 */
export function setupLSPDiagnostics(
	monacoInstance: typeof monaco,
): monaco.IDisposable {
	const lspClient = getLSPClient();
	if (!lspClient) {
		logger.warn("LSP client not available for diagnostics");
		return { dispose: () => {} };
	}

	// Listen for textDocument/publishDiagnostics notifications from LSP server
	const disposable = lspClient.onNotification(
		"textDocument/publishDiagnostics",
		(params: LSPDiagnostic) => {
			try {
				const uri = monacoInstance.Uri.parse(params.uri);
				const model = monacoInstance.editor.getModel(uri);

				if (!model) {
					// Model might have been closed, this is normal
					return;
				}

				// Convert LSP diagnostics to Monaco markers
				const markers: monaco.editor.IMarkerData[] = params.diagnostics
					// Filter out false positives for Writer framework globals
					.filter(
						(diagnostic) =>
							!isWriterFrameworkGlobalError(diagnostic),
					)
					.map((diagnostic) => ({
						severity: convertSeverity(
							diagnostic.severity,
							monacoInstance,
						),
						message: diagnostic.message,
						source: diagnostic.source || "pylsp",
						code: diagnostic.code?.toString(),
						startLineNumber: diagnostic.range.start.line + 1, // LSP is 0-based, Monaco is 1-based
						startColumn: diagnostic.range.start.character + 1,
						endLineNumber: diagnostic.range.end.line + 1,
						endColumn: diagnostic.range.end.character + 1,
					}));

				// Set markers on the model (this displays red/yellow squiggly lines)
				monacoInstance.editor.setModelMarkers(
					model,
					"pylsp", // Owner ID
					markers,
				);
			} catch (error) {
				logger.error("Failed to process LSP diagnostics:", error);
			}
		},
	);

	return disposable;
}

/**
 * Sets the diagnostics for a specific model.
 *
 * @param monacoInstance - The Monaco Editor API instance
 * @param model - The Monaco model to set diagnostics for
 * @param markers - The markers to set for the model
 */
export const setModelDiagnostics = (
	monacoInstance: typeof monaco,
	model: monaco.editor.ITextModel,
	markers: monaco.editor.IMarkerData[],
) => monacoInstance.editor.setModelMarkers(model, "pylsp", markers);
