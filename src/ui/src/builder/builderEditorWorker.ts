import * as monaco from "monaco-editor";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import cssWorker from "monaco-editor/esm/vs/language/css/css.worker?worker";
import htmlWorker from "monaco-editor/esm/vs/language/html/html.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";

if (!monaco.languages.getLanguages().some((lang) => lang.id === "python")) {
	monaco.languages.register({ id: "python" });
}

// Worker loader type
export type WorkerLoader = () => Worker;

// Define worker loaders for different language services
const workerLoaders: Partial<Record<string, WorkerLoader>> = {
	TextEditorWorker: () =>
		new Worker(
			new URL(
				"monaco-editor/esm/vs/editor/editor.worker.js",
				import.meta.url,
			),
			{ type: "module" },
		),
	TextMateWorker: () =>
		new Worker(
			new URL(
				"@codingame/monaco-vscode-textmate-service-override/worker",
				import.meta.url,
			),
			{ type: "module" },
		),
};

// MonacoEnvironment global configuration
self.MonacoEnvironment = {
	getWorker(_moduleId: string, label: string) {
		// Check if we have a specific worker loader for this label
		const workerFactory = workerLoaders[label];
		if (workerFactory != null) {
			return workerFactory();
		}

		// Fallback to built-in Monaco workers for standard languages
		if (label === "json") {
			return new jsonWorker();
		}
		if (label === "css" || label === "scss" || label === "less") {
			return new cssWorker();
		}
		if (label === "html" || label === "handlebars" || label === "razor") {
			return new htmlWorker();
		}
		if (label === "typescript" || label === "javascript") {
			return new tsWorker();
		}

		// Default editor worker
		return new editorWorker();
	},
};

monaco.languages.typescript.typescriptDefaults.setEagerModelSync(true);
