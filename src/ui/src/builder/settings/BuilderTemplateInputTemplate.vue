<template>
	<WdsTextInputLayout
		:left-icon
		:right-icon
		:invalid
		:variant
		class="BuilderTemplateInputTemplate"
		:class="{
			'BuilderTemplateInputTemplate--singleline': !multiline,
			'BuilderTemplateInputTemplate--multiline': multiline,
		}"
		@right-icon-click="$emit('rightIconClick')"
		@click="focus"
	>
		<BuilderTemplateEditor
			ref="input"
			class="BuilderTemplateInputTemplate__input"
			:multiline
			:model-value="model"
			@update:model-value="onChange"
		/>
	</WdsTextInputLayout>
</template>

<script setup lang="ts">
import { onMounted, PropType, useTemplateRef } from "vue";
import WdsTextInputLayout from "@/wds/WdsTextInputLayout.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BuilderTemplateEditor = defineAsyncComponentWithLoader({
	loader: () => import("../templateEditor/BuilderTemplateEditor.vue"),
});

const model = defineModel({ type: String });

const props = defineProps({
	leftIcon: { type: String, required: false, default: undefined },
	rightIcon: { type: String, required: false, default: undefined },
	invalid: { type: Boolean, required: false },
	variant: { type: String as PropType<"ghost">, default: undefined },
	autofocus: { type: Boolean },
	multiline: { type: Boolean, required: false },
});

const emit = defineEmits({
	rightIconClick: () => true,
	input: (event: InputEvent) => !!event,
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

async function onChange(value: string) {
	model.value = value;
	emit("input", {
		target: { value },
	} as unknown as InputEvent);
}

function setSelectionStart(value: number) {
	input.value?.setSelectionStart(value);
}
function setSelectionEnd(value: number) {
	input.value?.setSelectionEnd(value);
}

function getSelection() {
	return input.value?.getSelection();
}

function focus() {
	input.value?.focus();
}
</script>

<style scoped>
.BuilderTemplateInputTemplate__input {
	background: transparent;
	font-size: 14px;
	border: none;
	width: 100%;
	min-height: 21px;
	height: 100%;
}
.BuilderTemplateInputTemplate__input:focus {
	outline: none;
}
.BuilderTemplateInputTemplate--multiline .BuilderTemplateInputTemplate__input {
	min-height: 64px;
	line-height: 26px;
}

.BuilderTemplateInputTemplate--singleline {
	padding-top: 6px;
	padding-bottom: 6px;
}
.BuilderTemplateInputTemplate--singleline .BuilderTemplateInputTemplate__input {
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
</style>
