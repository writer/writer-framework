<script setup lang="ts">
import { PropType } from "vue";
import { WdsDropdownMenuOption } from "./WdsDropdownMenu.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";

defineProps({
	selected: { type: Boolean, required: false },
	option: {
		type: Object as PropType<WdsDropdownMenuOption>,
		required: true,
	},
	hideIcons: { type: Boolean, required: false },
});
</script>

<template>
	<button
		class="WdsDropdownMenu__item"
		:class="{
			'WdsDropdownMenu__item--selected': selected,
			'WdsDropdownMenu__item--hideIcon': hideIcons,
			'WdsDropdownMenu__item--danger': option.variant === 'danger',
		}"
		:data-automation-key="option.value"
		:disabled="option.disabled"
	>
		<template v-if="!hideIcons">
			<div
				v-if="Array.isArray(option.icon)"
				class="WdsDropdownMenu__item__icon WdsDropdownMenu__item__icon--img"
			>
				<SharedImgWithFallback :urls="option.icon" />
			</div>
			<i
				v-else-if="option.icon"
				class="material-symbols-outlined WdsDropdownMenu__item__icon"
				:class="{
					'WdsDropdownMenu__item__icon--iconColor': option.iconColor,
				}"
				:style="
					option.iconColor
						? { backgroundColor: option.iconColor }
						: undefined
				"
				>{{ option.icon }}</i
			>
		</template>
		<div
			class="WdsDropdownMenu__item__label"
			:data-writer-tooltip="option.label"
			data-writer-tooltip-strategy="overflow"
		>
			<span>{{ option.label }}</span>
			<span
				v-if="option.shortcut"
				class="WdsDropdownMenu__item__label__shortcut"
				>{{ option.shortcut }}</span
			>
		</div>
		<div
			v-if="option.detail"
			class="WdsDropdownMenu__item__detail"
			:data-writer-tooltip="option.detail"
			data-writer-tooltip-strategy="overflow"
		>
			{{ option.detail }}
		</div>
		<div class="WdsDropdownMenu__item__action">
			<i v-if="selected" class="material-symbols-outlined"> check </i>
			<slot v-else name="action" />
		</div>
	</button>
</template>

<style lang="css" scoped>
.WdsDropdownMenu__item {
	background-color: transparent;
	border: none;
	display: block;
	width: 100%;

	display: grid;
	grid-template-columns: 1fr auto;
	column-gap: 8px;
	align-items: center;

	border-radius: 4px;

	padding: 8px;
	font-weight: 400;
	font-size: 0.75rem;
	color: var(--wdsColorGray6);
	cursor: pointer;
	transition: all 0.2s;
	pointer-events: all;
}
.WdsDropdownMenu__item:disabled {
	opacity: 40%;
	cursor: not-allowed !important;
}
.WdsDropdownMenu__item:has(.WdsDropdownMenu__item__icon) {
	grid-template-columns: auto 1fr auto;
}
.WdsDropdownMenu__item:has(.WdsDropdownMenu__item__icon)
	.WdsDropdownMenu__item__detail {
	grid-column-start: 2;
}
.WdsDropdownMenu__item__icon {
	grid-row-start: 1;
	grid-row-end: -1;
	display: flex;
	align-items: center;
}

.WdsDropdownMenu__item:hover {
	cursor: pointer;
	background-color: var(--wdsColorBlue1);
}

.WdsDropdownMenu__item--selected {
	background-color: var(--wdsColorBlue2);
}
.WdsDropdownMenu__item--hideIcon {
	grid-template-columns: 1fr auto;
}
.WdsDropdownMenu__item--danger {
	color: var(--wdsColorOrange5);
}

.WdsDropdownMenu__item__detail,
.WdsDropdownMenu__item__label {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
	text-align: left;
}

.WdsDropdownMenu__item__label {
	display: flex;
	justify-content: space-between;
	gap: 4px;
	width: 100%;
}
.WdsDropdownMenu__item__label__shortcut {
	color: var(--wdsColorGray4);
}

.WdsDropdownMenu__item:has(.WdsDropdownMenu__item__detail) {
	grid-template-rows: auto auto;
}

.WdsDropdownMenu__item__detail {
	grid-row: 2;
	color: var(--wdsColorGray4);
}

.WdsDropdownMenu__item__icon--iconColor {
	display: block;
	line-height: 18px;
	height: 18px;
	width: 18px;
	border-radius: 4px;
}
.WdsDropdownMenu__item__action {
	grid-row: 1 / -1;
	grid-column: -1;
	display: flex;
	align-items: center;
}
</style>
