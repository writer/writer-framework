/**
 * Composable for integrating monacopilot AI code completions
 * with Monaco Editor instances.
 */
import type * as monaco from "monaco-editor";

/**
 * Registers AI-powered code completion for a Monaco Editor instance.
 *
 * @param monacoInstance - The Monaco Editor API instance
 * @param editor - The standalone code editor instance
 * @param language - The programming language (e.g., 'python', 'javascript', 'typescript')
 * @returns Cleanup function to unregister the completion provider
 */
export async function useMonacopilot(
	monacoInstance: typeof monaco,
	editor: monaco.editor.IStandaloneCodeEditor,
	language: string,
): Promise<() => void> {
	try {
		// Dynamically import monacopilot only when needed
		const { registerCompletion } = await import("monacopilot");

		// Register the completion provider with monacopilot
		const disposable = registerCompletion(monacoInstance, editor, {
			language: language,
			// API endpoint for code completions
			endpoint: "/api/code-completion",
			technologies: ["writer-agent-builder"],
			// Optional: Trigger completion automatically
			trigger: "onIdle",
		});

		// Return cleanup function
		return () => {
			if (disposable && typeof disposable.deregister === "function") {
				disposable.deregister();
			}
		};
	} catch (error) {
		console.error("Failed to register monacopilot:", error);
		// Return no-op cleanup function on error
		return () => {};
	}
}
