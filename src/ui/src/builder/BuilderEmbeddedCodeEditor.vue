<template>
	<div
		ref="rootEl"
		class="BuilderEmbeddedCodeEditor"
		:class="{
			'BuilderEmbeddedCodeEditor--full': variant === 'full',
			'BuilderEmbeddedCodeEditor--halfScreen': variant === 'half-screen',
			'BuilderEmbeddedCodeEditor--singleLine': variant === 'single-line',
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
	PropType,
	toRefs,
	useTemplateRef,
	watch,
} from "vue";

const rootEl = useTemplateRef("rootEl");
const editorContainerEl = useTemplateRef("editorContainerEl");
const resizeObserver = new ResizeObserver(updateDimensions);
let editor: monaco.editor.IStandaloneCodeEditor = null;

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
	if (editor.getValue() == newCode) return;
	editor.getModel().setValue(newCode);
});

watch(language, () => {
	monaco.editor.setModelLanguage(editor.getModel(), language.value);
});

onMounted(() => {
	editor = monaco.editor.create(editorContainerEl.value, {
		value: modelValue.value ?? "",
		language: props.language,
		readOnly: props.disabled,
		fixedOverflowWidgets: true,
		...VARIANTS_SETTINGS[props.variant],
	});
	editor.getModel().onDidChangeContent(() => {
		const newCode = editor.getValue();
		emit("update:modelValue", newCode);
	});
	resizeObserver.observe(rootEl.value);

	// when in modal, focus the editor and set the cursor to the last line
	if (props.variant === "half-screen") {
		editor.focus();
		editor.setPosition({
			lineNumber: editor.getModel().getLineCount(),
			column: editor
				.getModel()
				.getLineLastNonWhitespaceColumn(
					editor.getModel().getLineCount(),
				),
		});
	}
});

function updateDimensions() {
	editor.layout();
}

onUnmounted(() => {
	editor.dispose();
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
