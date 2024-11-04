<template>
	<div class="BuilderEmbeddedCodeEditor">
		<div ref="editorContainerEl" class="editorContainer"></div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";
import "./builderEditorWorker";
import { onMounted, onUnmounted, ref, toRefs, watch } from "vue";

const editorContainerEl = ref<HTMLElement>(null);
let editor: monaco.editor.IStandaloneCodeEditor = null;

const props = defineProps<{
	language: string;
	variant: "full" | "minimal";
	modelValue: string;
	disabled?: boolean;
}>();

const { modelValue, disabled } = toRefs(props);
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

onMounted(() => {
	editor = monaco.editor.create(editorContainerEl.value, {
		value: modelValue.value,
		language: props.language,
		...VARIANTS_SETTINGS[props.variant],
	});
	editor.getModel().onDidChangeContent(() => {
		const newCode = editor.getValue();
		emit("update:modelValue", newCode);
	});
	window.addEventListener("resize", updateDimensions.bind(this));
});

function updateDimensions() {
	editor.layout();
}

onUnmounted(() => {
	editor.dispose();
	window.removeEventListener("resize", updateDimensions.bind(this));
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderEmbeddedCodeEditor {
	height: 100%;
	width: 100%;
	min-height: 200px;
}

.editorContainer {
	min-height: 200px;
	width: 100%;
	height: 100%;
}
</style>
