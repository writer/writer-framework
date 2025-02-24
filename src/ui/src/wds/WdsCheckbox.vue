<script lang="ts" setup>
import { computed, defineProps, useId } from "vue";

const props = defineProps({
	label: { type: String, required: false, default: undefined },
	detail: { type: String, required: false, default: undefined },
	disabled: { type: Boolean, required: false },
});

const id = useId();

const checked = defineModel({ type: Boolean, default: false });

const classes = computed(() =>
	[
		props.disabled ? "WdsCheckbox--disabled" : undefined,
		checked.value ? "WdsCheckbox--checked" : undefined,
	].filter(Boolean),
);
function onChange(event: InputEvent) {
	checked.value = (event.target as HTMLInputElement).checked;
}
</script>

<template>
	<label
		:for="id"
		class="WdsCheckbox"
		:class="classes"
		@mousedown.prevent
		@click.prevent="checked = !checked"
	>
		<div class="WdsCheckbox__checkbox">
			<i class="WdsCheckbox__checkbox__check material-symbols-outlined"
				>check</i
			>
		</div>
		<span v-if="label" class="WdsCheckbox__label">{{ label }}</span>
		<span v-if="detail" class="WdsCheckbox__detail">{{ detail }}</span>
		<input
			:id="id"
			type="checkbox"
			:checked="checked"
			:disabled="disabled"
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
}
.WdsCheckbox__checkbox {
	border: 1px solid var(--wdsColorGray4);
	width: 18px;
	height: 18px;

	border-radius: 4px;
	grid-row-start: 1;
	grid-row-end: -1;
}
.WdsCheckbox--checked .WdsCheckbox__checkbox {
	background-color: var(--wdsColorBlue5);
	font-weight: bold;
}

.WdsCheckbox__checkbox__check {
	display: none;
}

.WdsCheckbox:hover:not(.WdsCheckbox--checked) .WdsCheckbox__checkbox__check {
	display: block;
	color: var(--wdsColorGray4);
}
.WdsCheckbox--checked .WdsCheckbox__checkbox__check {
	display: block;
	color: var(--wdsColorWhite);
}

.WdsCheckbox__detail,
.WdsCheckbox__label {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
	text-align: left;
}

.WdsCheckbox:has(.WdsCheckbox__detail) {
	grid-template-rows: auto auto;
}

.WdsCheckbox__detail {
	color: var(--wdsColorGray4);
}

.WdsCheckbox input {
	display: none;
}
</style>
