<template>
	<div
		ref="rootEl"
		class="BuilderEmbeddedCodeEditor"
		:class="{
			'BuilderEmbeddedCodeEditor--full': variant === 'full',
			'BuilderEmbeddedCodeEditor--halfScreen': variant === 'half-screen',
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

const props = defineProps({
	language: { type: String, required: false, default: "" },
	variant: {
		type: String as PropType<"full" | "minimal" | "half-screen">,
		required: true,
	},
	modelValue: { type: String, required: false, default: "" },
	disabled: { type: Boolean, required: false },
});

const { modelValue, disabled, language } = toRefs(props);
const emit = defineEmits(["update:modelValue"]);

const VARIANTS_SETTINGS: Record<
	string,
	Partial<monaco.editor.IStandaloneEditorConstructionOptions>
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

.editorContainer {
	min-height: inherit;
	width: 100%;
	height: 100%;
	overflow: hidden;
}
</style>
