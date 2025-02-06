<template>
	<div
		v-if="leftIcon"
		v-bind="$attrs"
		class="WdsTextInput WdsTextInput--leftIcon colorTransformer"
		:aria-invalid="invalid"
		@click="input.focus()"
	>
		<i class="material-symbols-outlined">{{ leftIcon }}</i>
		<input ref="input" v-model="model" v-bind="$attrs" />
	</div>
	<input
		v-else
		v-bind="$attrs"
		ref="input"
		v-model="model"
		:aria-invalid="invalid"
		class="WdsTextInput colorTransformer"
	/>
</template>

<script setup lang="ts">
import { ref } from "vue";

const model = defineModel({ type: String });

// disable attributes inheritance to apply attr to nested input
defineOptions({ inheritAttrs: false });

defineProps({
	leftIcon: { type: String, required: false, default: undefined },
	invalid: { type: Boolean, required: false },
});

defineExpose({
	focus,
	getSelection,
	value: model,
	setSelectionEnd,
	setSelectionStart,
});

const input = ref<HTMLInputElement>();

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
@import "@/renderer/colorTransformations.css";

.WdsTextInput {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 14px;
	outline: none;
	color: var(--primaryTextColor);
	background: transparent;
}

.WdsTextInput:focus,
.WdsTextInput--leftIcon:focus-within {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.WdsTextInput--leftIcon {
	cursor: pointer;
	display: flex;
	align-items: center;
	gap: 8px;
}

.WdsTextInput--leftIcon i {
	color: var(--wdsColorGray5);
}

.WdsTextInput--leftIcon input {
	font-size: 14px;
	border: none;
	background: transparent;
}
.WdsTextInput--leftIcon input:focus {
	border: none;
	box-shadow: none;
	outline: none;
}

.WdsTextInput[aria-invalid="true"] {
	border-color: var(--wdsColorOrange5);
}
</style>
