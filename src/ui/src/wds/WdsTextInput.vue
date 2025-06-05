<template>
	<div
		v-if="leftIcon || enableClearButton || rightIcon"
		class="WdsTextInput WdsTextInput--leftIcon colorTransformer"
		:class="{ 'WdsTextInput--ghost': variant === 'ghost' }"
		v-bind="$attrs"
		:aria-invalid="invalid"
		:style="{
			gridTemplateColumns: gridTemplateColumns,
		}"
		@click="focus"
	>
		<i v-if="leftIcon" class="material-symbols-outlined">{{ leftIcon }}</i>
		<input
			ref="input"
			v-model="model"
			:autofocus="autofocus"
			v-bind="$attrs"
		/>
		<p v-if="rightText" class="WdsTextInput__rightText">{{ rightText }}</p>
		<button
			v-if="rightIcon && model"
			class="WdsTextInput__rightIcon"
			type="button"
			@click="$emit('rightIconClick')"
		>
			<i class="material-symbols-outlined">{{ rightIcon }}</i>
		</button>
	</div>
	<input
		v-else
		v-bind="$attrs"
		ref="input"
		v-model="model"
		:autofocus="autofocus"
		:aria-invalid="invalid"
		class="WdsTextInput colorTransformer"
		:class="{ 'WdsTextInput--ghost': variant === 'ghost' }"
	/>
</template>

<script setup lang="ts">
import { computed, onMounted, PropType, useTemplateRef } from "vue";

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

const gridTemplateColumns = computed(() =>
	[
		props.leftIcon ? "auto" : undefined,
		"1fr",
		props.rightText ? "auto" : undefined,
		props.rightIcon ? "auto" : undefined,
	]
		.filter(Boolean)
		.join(" "),
);

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
	transition: box-shadow ease-in-out 0.2s;
}

.WdsTextInput:focus,
.WdsTextInput--leftIcon:focus-within {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.WdsTextInput--ghost {
	border-color: transparent;
	background-color: transparent;
	transition:
		box-shadow,
		background-color,
		border-color ease-in-out 0.2s;
}
.WdsTextInput--ghost:disabled {
	cursor: not-allowed;
}
.WdsTextInput--ghost:not(:disabled):hover {
	background-color: transparent;
	border-color: var(--wdsColorBlue3);
}
.WdsTextInput--ghost:not(:disabled):focus,
.WdsTextInput--ghost:not(:disabled):focus-within {
	background-color: transparent;
}

.WdsTextInput--leftIcon {
	cursor: pointer;
	display: grid;
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
	width: 100%;
}
.WdsTextInput--leftIcon input:focus {
	border: none;
	box-shadow: none;
	outline: none;
}

.WdsTextInput__rightIcon {
	border: none;
	background-color: transparent;
	display: flex;
	align-items: center;
	cursor: pointer;
}

.WdsTextInput__rightText {
	padding-left: 8px;
	border-left: 2px solid var(--separatorColor);
}

.WdsTextInput[aria-invalid="true"] {
	border-color: var(--wdsColorOrange5);
}
</style>
