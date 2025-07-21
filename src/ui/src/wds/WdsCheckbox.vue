<script lang="ts" setup>
import { useId } from "vue";
import WdsIcon from "./WdsIcon.vue";

defineProps({
	label: { type: String, required: false, default: undefined },
	detail: { type: String, required: false, default: undefined },
	disabled: { type: Boolean, required: false },
	invalid: { type: Boolean, default: false },
});

const id = useId();

const checked = defineModel({ type: Boolean, default: false });

function onChange(event: InputEvent) {
	checked.value = (event.target as HTMLInputElement).checked;
}
</script>

<template>
	<label
		:for="id"
		class="WdsCheckbox"
		:class="{
			'WdsCheckbox--disabled': disabled,
			'WdsCheckbox--invalid': invalid,
			'WdsCheckbox--checked': checked,
		}"
		@mousedown.prevent
	>
		<div class="WdsCheckbox__checkbox">
			<WdsIcon name="check" class="WdsCheckbox__checkbox__check" />
		</div>
		<span v-if="label" class="WdsCheckbox__label">{{ label }}</span>
		<span v-if="detail" class="WdsCheckbox__detail">{{ detail }}</span>
		<input
			:id="id"
			type="checkbox"
			:checked="checked"
			:disabled="disabled"
			:aria-invalid="invalid"
			@change.stop="onChange"
		/>
	</label>
</template>

<style lang="css" scoped>
.WdsCheckbox {
	display: grid;
	grid-template-columns: auto 1fr;
	grid-template-rows: auto;
	align-items: center;
	column-gap: 12px;
	row-gap: 2px;
	cursor: pointer;
	text-align: center;
}
.WdsCheckbox--disabled {
	opacity: 40%;
	cursor: not-allowed;
}

.WdsCheckbox--invalid .WdsCheckbox__checkbox {
	border-color: var(--wdsColorOrange5);
}

.WdsCheckbox--invalid .WdsCheckbox__label {
	color: var(--wdsColorOrange5);
}

.WdsCheckbox__checkbox {
	border: 1px solid var(--wdsColorGray4);
	width: 18px;
	height: 18px;
	display: flex;
	align-items: center;
	justify-content: center;

	border-radius: 4px;
	grid-row-start: 1;
	grid-row-end: -1;
}
.WdsCheckbox--checked .WdsCheckbox__checkbox {
	background-color: var(--wdsColorBlue5);
	font-weight: bold;
}

:deep(.WdsCheckbox__checkbox__check) {
	display: none;
}

.WdsCheckbox:hover:not(.WdsCheckbox--checked):not(.WdsCheckbox--disabled)
	:deep(.WdsCheckbox__checkbox__check) {
	display: block;
	color: var(--wdsColorGray4);
}

.WdsCheckbox--checked :deep(.WdsCheckbox__checkbox__check) {
	display: block;
	color: var(--wdsColorWhite);
}

.WdsCheckbox__label {
	font-size: 14px;
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}

.WdsCheckbox__detail {
	font-size: 12px;
}

.WdsCheckbox__label,
.WdsCheckbox__detail {
	line-height: 180%;
	text-align: left;
}

.WdsCheckbox:has(.WdsCheckbox__detail) {
	align-items: start;
	grid-template-rows: auto auto;
}

.WdsCheckbox:has(.WdsCheckbox__detail) .WdsCheckbox__checkbox {
	margin-top: 14px;
}

.WdsCheckbox__detail {
	color: var(--wdsColorGray4);
}

.WdsCheckbox input {
	display: none;
}
</style>
