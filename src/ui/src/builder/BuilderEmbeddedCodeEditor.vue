<template>
	<div
		ref="rootEl"
		class="BuilderEmbeddedCodeEditor"
		:class="{
			'BuilderEmbeddedCodeEditor--full': props.variant === 'full',
			'BuilderEmbeddedCodeEditor--halfScreen':
				props.variant === 'half-screen',
			'BuilderEmbeddedCodeEditor--singleLine':
				props.variant === 'single-line',
		}"
	>
		<div ref="editorContainerEl" class="editorContainer"></div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";
import "./builderEditorWorker";
import {
	onMounted,
	onUnmounted,
	type PropType,
	toRefs,
	useTemplateRef,
	watch,
} from "vue";
import { syncModelWithLSP } from "./lsp/lspModelSync";
import { setModelDiagnostics, setupLSPDiagnostics } from "./lsp/lspDiagnostics";
import { useMonacopilot } from "../composables/useMonacopilot";
import { useLogger } from "@/composables/useLogger";
import { useCodeEditorSettings } from "@/composables/useCodeEditorSettings";

const rootEl = useTemplateRef("rootEl");
const editorContainerEl = useTemplateRef("editorContainerEl");
const resizeObserver = new ResizeObserver(updateDimensions);
let editor: monaco.editor.IStandaloneCodeEditor = null;
let lspSyncDisposable: monaco.IDisposable | null = null;
let diagnosticsDisposable: monaco.IDisposable | null = null;
let monacopilotCleanup: (() => void) | null = null;

const { diagnosticsEnabled, aiCompletionEnabled } = useCodeEditorSettings();

type EditorVariant = "full" | "minimal" | "half-screen" | "single-line";

const props = defineProps({
	language: { type: String, required: false, default: "" },
	variant: {
		type: String as PropType<EditorVariant>,
		required: true,
	},
	modelValue: { type: String, required: false, default: "" },
	disabled: { type: Boolean, required: false },
});

const { modelValue, disabled, language } = toRefs(props);
const emit = defineEmits(["update:modelValue"]);

const logger = useLogger();

const VARIANTS_SETTINGS: Partial<
	Record<
		EditorVariant,
		Partial<monaco.editor.IStandaloneEditorConstructionOptions>
	>
> = {
	full: {
		minimap: {
			enabled: false,
		},
		tabCompletion: "on",
	},
	minimal: {
		minimap: {
			enabled: false,
		},
		lineNumbers: "off",
		folding: false,
	},
	"single-line": {
		minimap: {
			enabled: false,
		},
		wordWrap: "off",
		lineNumbers: "off",
		lineNumbersMinChars: 0,
		overviewRulerLanes: 0,
		overviewRulerBorder: false,
		lineDecorationsWidth: 0,
		hideCursorInOverviewRuler: true,
		glyphMargin: false,
		folding: false,
		scrollBeyondLastColumn: 0,
		scrollbar: { horizontal: "auto", vertical: "hidden" },
		renderLineHighlight: "none",
		find: {
			addExtraSpaceOnTop: false,
			autoFindInSelection: "never",
		},
	},
};

watch(disabled, (isNewDisabled) => {
	if (isNewDisabled) {
		editor.updateOptions({ readOnly: true });
		return;
	}
	editor.updateOptions({ readOnly: false });
});

watch(modelValue, (newCode) => {
	if (!editor || editor.getValue() === newCode) return;
	editor.getModel().setValue(newCode);
});

watch(language, (newLang) => {
	if (!editor) return;
	const model = editor.getModel();
	if (model.getLanguageId() === newLang) return;

	// Dispose old LSP sync before changing language
	if (lspSyncDisposable) {
		lspSyncDisposable.dispose();
		lspSyncDisposable = null;
	}

	// Change language
	monaco.editor.setModelLanguage(model, newLang);

	// Re-sync if new language is Python
	if (newLang === "python") {
		try {
			lspSyncDisposable = syncModelWithLSP(model);
		} catch (error) {
			logger.error("Failed to re-sync model with LSP:", error);
		}
	}
});

watch(diagnosticsEnabled, (enabled) => {
	if (
		!editor ||
		language.value !== "python" ||
		props.variant === "single-line"
	) {
		return;
	}

	const model = editor.getModel();
	if (model && language.value === "python") {
		diagnosticsDisposable?.dispose();
		if (enabled) {
			diagnosticsDisposable = setupLSPDiagnostics(monaco);
		}
		model.setValue(model.getValue());
	}
});

// Watch AI completion setting changes
watch(aiCompletionEnabled, async (enabled) => {
	if (
		!editor ||
		language.value !== "python" ||
		props.variant === "single-line"
	)
		return;

	if (enabled) {
		// Enable AI completion
		if (!monacopilotCleanup) {
			try {
				monacopilotCleanup = await useMonacopilot(
					monaco,
					editor,
					language.value,
				);
			} catch (error) {
				logger.error("Failed to enable AI completion:", error);
			}
		}
	} else {
		// Disable AI completion
		if (monacopilotCleanup) {
			monacopilotCleanup();
			monacopilotCleanup = null;
		}
	}
});

onMounted(async () => {
	// Create model with proper URI for LSP
	const modelUri = monaco.Uri.parse(`inmemory://model/${Date.now()}.py`);
	const model = monaco.editor.createModel(
		modelValue.value ?? "",
		language.value || "python",
		language.value === "python" ? modelUri : undefined,
	);

	editor = monaco.editor.create(editorContainerEl.value as HTMLElement, {
		model: model,
		readOnly: props.disabled,
		fixedOverflowWidgets: true,
		quickSuggestions: {
			other: true,
			comments: true,
			strings: true,
		},
		...VARIANTS_SETTINGS[props.variant],
	});

	model.onDidChangeContent(() => {
		const newCode = editor.getValue();
		emit("update:modelValue", newCode);
	});

	resizeObserver.observe(rootEl.value as Element);

	// Manually sync model with LSP for Python language
	// This is required because we're in a browser (no filesystem)
	if (language.value === "python" && props.variant !== "single-line") {
		try {
			lspSyncDisposable = syncModelWithLSP(model);
		} catch (error) {
			logger.error("Failed to sync model with LSP:", error);
		}

		// Register AI-powered code completions (if AI completion enabled)
		if (aiCompletionEnabled.value) {
			try {
				monacopilotCleanup = await useMonacopilot(
					monaco,
					editor,
					language.value,
				);
			} catch (error) {
				logger.error("Failed to initialize monacopilot:", error);
			}
		}

		diagnosticsDisposable?.dispose();
		if (diagnosticsEnabled.value) {
			diagnosticsDisposable = setupLSPDiagnostics(monaco);
		}
	}

	// when in modal, focus the editor and set the cursor to the last line
	if (props.variant === "half-screen") {
		editor.focus();
		editor.setPosition({
			lineNumber: model.getLineCount(),
			column: model.getLineLastNonWhitespaceColumn(model.getLineCount()),
		});
	}
});

function updateDimensions() {
	editor.layout();
}

onUnmounted(() => {
	// Clean up LSP sync
	if (lspSyncDisposable) {
		lspSyncDisposable.dispose();
		lspSyncDisposable = null;
	}

	const model = editor?.getModel();

	// Clear diagnostics before disposing model
	if (model && language.value === "python") {
		setModelDiagnostics(monaco, model, []);
	}

	if (editor) {
		editor.dispose();
	}
	if (model) {
		model.dispose();
	}
	if (monacopilotCleanup) {
		monacopilotCleanup();
	}
	if (diagnosticsDisposable) {
		diagnosticsDisposable.dispose();
		diagnosticsDisposable = null;
	}
	resizeObserver.disconnect();
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderEmbeddedCodeEditor {
	height: 100%;
	width: 100%;
	min-height: 100px;
}

.BuilderEmbeddedCodeEditor--full {
	min-height: 300px;
}

.BuilderEmbeddedCodeEditor--halfScreen {
	min-height: 50vh;
}

.BuilderEmbeddedCodeEditor--singleLine {
	min-height: 35px;
	max-height: 35px;
	height: 35px;
	padding: 8.5px 12px 8.5px 12px;
	display: flex;
	align-items: center;
}

.BuilderEmbeddedCodeEditor--singleLine .editorContainer {
	min-height: 18px;
}

.editorContainer {
	min-height: inherit;
	width: 100%;
	height: 100%;
	overflow: hidden;
}
</style>
