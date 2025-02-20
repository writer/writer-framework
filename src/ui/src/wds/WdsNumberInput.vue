<template>
	<div class="WdsNumberInput colorTransformer" :class="props.class">
		<input
			ref="input"
			v-model="model"
			class="WdsNumberInput__input"
			v-bind="$attrs"
			type="number"
			@focusout="$emit('focusout', model)"
		/>
		<div class="WdsNumberInput__right">
			<button
				class="WdsNumberInput__right__arrow"
				type="button"
				@click.prevent="increase(step)"
				@pointerdown.prevent
			>
				<span class="WdsNumberInput__right__arrow__up"></span>
			</button>
			<button
				class="WdsNumberInput__right__arrow"
				type="button"
				@click.prevent="increase(-step)"
				@pointerdown.prevent
			>
				<span class="WdsNumberInput__right__arrow__down"></span>
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const model = defineModel({
	type: Number,
	required: false,
	default: undefined,
});

defineEmits({
	focusout: (value: number) => typeof value === "number",
});

// disable attributes inheritance to apply attr to nested input
defineOptions({ inheritAttrs: false });

const props = defineProps({
	step: { type: Number, default: 1 },
	class: { type: String, default: undefined },
});

defineExpose({ focus });

const input = ref<HTMLInputElement>();

function increase(step: number) {
	model.value = (model.value ?? 0) + step;
	focus();
}

function focus() {
	input.value?.focus();
}
</script>

<style scoped>
@import "@/renderer/colorTransformations.css";

.WdsNumberInput {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	background-color: var(--wdsColorWhite);
	border-radius: 8px;
	outline: none;
	color: var(--primaryTextColor);

	display: grid;
	grid-template-columns: minmax(0px, 1fr) auto;
	gap: 8px;
	cursor: pointer;
	align-items: center;
}

.WdsNumberInput:focus,
.WdsNumberInput:focus-within {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
.WdsNumberInput__input,
.WdsNumberInput__right {
	padding: 8.5px 12px 8.5px 12px;
}

.WdsNumberInput__input {
	font-size: inherit;
	border: none;
	background: transparent;
	-webkit-appearance: none;
	-moz-appearance: textfield;
	appearance: textfield;
	width: 100%;
}
.WdsNumberInput__input:focus {
	border: none;
	box-shadow: none;
	outline: none;
}

.WdsNumberInput__right {
	display: grid;
	grid-template-rows: auto auto;
	align-items: center;
	justify-content: center;
	border-left: 1px solid var(--separatorColor);
	height: 100%;
}

.WdsNumberInput__right__arrow {
	cursor: pointer;
	background-color: transparent;
	border: none;

	display: flex;
	align-items: center;
	justify-content: center;
	padding: 2px;
}
.WdsNumberInput__right__arrow__up {
	border-bottom: 4px solid;
	border-left: 4px solid transparent;
	border-right: 4px solid transparent;
	background: white;
	border-top: none;
}
.WdsNumberInput__right__arrow:hover .WdsNumberInput__right__arrow__up {
	border-bottom-color: var(--wdsColorGray3);
}

.WdsNumberInput__right__arrow__down {
	border-top: 4px solid;
	border-left: 4px solid transparent;
	border-right: 4px solid transparent;
	background: white;
	border-bottom: none;
}
.WdsNumberInput__right__arrow:hover .WdsNumberInput__right__arrow__down {
	border-top-color: var(--wdsColorGray3);
}
</style>
