<template>
	<textarea ref="input" v-model="model" :aria-invalid="invalid"></textarea>
</template>

<script setup lang="ts">
import { ref } from "vue";

const model = defineModel<string>();

defineProps({
	invalid: { type: Boolean, required: false },
});

defineExpose({
	focus,
	getSelection,
	value: model,
	setSelectionEnd,
	setSelectionStart,
});

const input = ref<HTMLTextAreaElement>();

function setSelectionStart(value: number) {
	if (input.value) input.value.selectionStart = value;
}
function setSelectionEnd(value: number) {
	if (input.value) input.value.selectionEnd = value;
}

function getSelection() {
	return {
		selectionStart: input.value?.selectionStart,
		selectionEnd: input.value?.selectionEnd,
	};
}

function focus() {
	input.value?.focus();
}
</script>

<style scoped>
textarea {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
	color: var(--primaryTextColor);
}

textarea:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
textarea[aria-invalid="true"] {
	border-color: var(--wdsColorOrange5);
}
</style>
