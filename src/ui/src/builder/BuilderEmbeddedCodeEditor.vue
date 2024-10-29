<template>
	<div ref="builderEditor" class="BuilderEmbeddedCodeEditor">
		<div ref="editorContainer" class="editorContainer"></div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";
import "./builderEditorWorker";
import { inject, onMounted, onUnmounted, Ref, ref, toRefs, watch } from "vue";
import injectionKeys from "../injectionKeys";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const builderEditor: Ref<HTMLElement> = ref(null);
const editorContainer: Ref<HTMLElement> = ref(null);
let editor: monaco.editor.IStandaloneCodeEditor = null;

// const editorCode = editor.getValue();

// <input
//     :value="props.modelValue"
//     @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
//   />

const props = defineProps<{
	modelValue: string;
}>();

const { modelValue } = toRefs(props);

const emit = defineEmits(["update:modelValue"]);

// watch(modelValue, (newCode) => {
//     const currentCode =
// 	editor.setValue(newCode);
// });

onMounted(() => {
	const targetEl = editorContainer.value;
	editor = monaco.editor.create(targetEl, {
		value: modelValue.value,
		language: "json",
		minimap: {
			enabled: false,
		},
		lineNumbers: "off",
		scrollbar: {
			vertical: "auto",
			horizontal: "auto",
		},
		fontSize: 12,
		folding: false,
		// theme: "",
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

.BuilderEditor {
}

.editorContainer {
	height: 200px;
}
</style>
