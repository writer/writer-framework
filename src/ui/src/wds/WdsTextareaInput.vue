<template>
	<textarea
		ref="input"
		v-model="model"
		:aria-invalid="invalid"
		:autofocus="autofocus"
	></textarea>
</template>

<script setup lang="ts">
import { onMounted, useTemplateRef } from "vue";

const model = defineModel<string>();

const props = defineProps({
	invalid: { type: Boolean, required: false },
	autofocus: { type: Boolean },
});

defineExpose({
	focus,
	getSelection,
	value: model,
	setSelectionEnd,
	setSelectionStart,
});

const input = useTemplateRef("input");

onMounted(() => {
	if (props.autofocus) focus();
});

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
