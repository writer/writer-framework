<template>
	<WdsTextInputLayout
		:left-icon
		:right-icon
		:invalid
		:variant
		:right-text
		class="WdsTextInput"
		@right-icon-click="$emit('rightIconClick')"
		@click="focus"
	>
		<input
			ref="input"
			v-model="model"
			class="WdsTextInput__input"
			:autofocus="autofocus"
			v-bind="$attrs"
		/>
	</WdsTextInputLayout>
</template>

<script setup lang="ts">
import { onMounted, PropType, useTemplateRef } from "vue";
import WdsTextInputLayout from "./WdsTextInputLayout.vue";

const model = defineModel({ type: String });

// disable attributes inheritance to apply attr to nested input
defineOptions({ inheritAttrs: false });

const props = defineProps({
	leftIcon: { type: String, required: false, default: undefined },
	rightIcon: { type: String, required: false, default: undefined },
	invalid: { type: Boolean, required: false },
	variant: { type: String as PropType<"ghost">, default: undefined },
	enableClearButton: { type: Boolean, required: false },
	rightText: { type: String, required: false, default: "" },
	autofocus: { type: Boolean },
});

defineEmits({
	rightIconClick: () => true,
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
.WdsTextInput__input {
	font-size: 14px;
	border: none;
	background: transparent;
	width: 100%;
}
.WdsTextInput__input:focus {
	border: none;
	box-shadow: none;
	outline: none;
}
</style>
