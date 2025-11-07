<script setup lang="ts">
import { computed, CSSProperties, PropType } from "vue";
import { WdsDropdownMenuOption } from "./WdsDropdownMenu.vue";
import WdsIcon from "./WdsIcon.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";

const props = defineProps({
	showCustomAction: { type: Boolean },
	selected: { type: Boolean, required: false },
	option: {
		type: Object as PropType<WdsDropdownMenuOption>,
		required: true,
	},
	hideIcons: { type: Boolean, required: false },
});

const style = computed<CSSProperties>(() => {
	const columns = [];
	if (!props.hideIcons && props.option.icon) {
		columns.push("auto");
	}
	columns.push("minmax(0, 1fr)");
	if (props.selected || props.showCustomAction) columns.push("auto");

	return {
		"grid-template-columns": columns.join(" "),
	};
});

const iconStyle = computed(() => {
	const style: CSSProperties = {};

	if (props.option.iconColor) {
		style.color = props.option.iconColor;
	}

	if (props.option.iconBgColor) {
		style["background-color"] = props.option.iconBgColor;
	}

	return Object.values(style).length > 0 ? style : undefined;
});
</script>

<template>
	<button
		class="WdsDropdownMenuItem"
		:class="{
			'WdsDropdownMenuItem--selected': selected,
			'WdsDropdownMenuItem--hideIcon': hideIcons,
			'WdsDropdownMenuItem--danger': option.variant === 'danger',
		}"
		:style
		:data-automation-key="option.value"
		:disabled="option.disabled"
	>
		<template v-if="!hideIcons">
			<div
				v-if="Array.isArray(option.icon)"
				class="WdsDropdownMenuItem__icon WdsDropdownMenuItem__icon--img"
			>
				<SharedImgWithFallback
					:urls="option.icon"
					:loader-max-width-px="18"
					:loader-max-height-px="18"
				/>
			</div>
			<div
				v-else-if="option.icon"
				class="WdsDropdownMenuItem__icon"
				:class="{
					'WdsDropdownMenuItem__icon--iconColor': iconStyle,
				}"
				:style="iconStyle"
			>
				<WdsIcon :name="option.icon" />
			</div>
		</template>
		<div
			class="WdsDropdownMenuItem__label"
			:data-writer-tooltip="option.label"
			data-writer-tooltip-strategy="overflow"
		>
			<span>{{ option.label }}</span>
			<span
				v-if="option.shortcut"
				class="WdsDropdownMenuItem__label__shortcut"
				>{{ option.shortcut }}</span
			>
		</div>
		<div
			v-if="option.detail"
			class="WdsDropdownMenuItem__detail"
			:data-writer-tooltip="option.detail"
			data-writer-tooltip-strategy="overflow"
		>
			{{ option.detail }}
		</div>
		<div
			v-if="selected || showCustomAction"
			class="WdsDropdownMenuItem__action"
		>
			<WdsIcon v-if="selected" name="check" />
			<slot v-else-if="showCustomAction" name="action" />
		</div>
	</button>
</template>

<style lang="css" scoped>
.WdsDropdownMenuItem {
	background-color: transparent;
	border: none;
	display: block;
	width: 100%;

	display: grid;
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
.WdsDropdownMenuItem:disabled {
	opacity: 40%;
	cursor: not-allowed !important;
}
.WdsDropdownMenuItem:has(.WdsDropdownMenuItem__icon)
	.WdsDropdownMenuItem__detail {
	grid-column-start: 2;
}
.WdsDropdownMenuItem__icon {
	grid-row-start: 1;
	grid-row-end: -1;
	display: flex;
	align-items: center;
}

.WdsDropdownMenuItem:hover {
	cursor: pointer;
	background-color: var(--wdsColorBlue1);
}

.WdsDropdownMenuItem--selected {
	background-color: var(--wdsColorBlue2);
}
.WdsDropdownMenuItem--danger {
	color: var(--wdsColorOrange5);
}

.WdsDropdownMenuItem__detail,
.WdsDropdownMenuItem__label,
.WdsDropdownMenuItem__label span {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
	text-align: left;
}

.WdsDropdownMenuItem__label {
	display: flex;
	justify-content: space-between;
	gap: 4px;
	width: 100%;
}
.WdsDropdownMenuItem__label__shortcut {
	color: var(--wdsColorGray4);
}

.WdsDropdownMenuItem:has(.WdsDropdownMenuItem__detail) {
	grid-template-rows: auto auto;
}

.WdsDropdownMenuItem__detail {
	grid-row: 2;
	color: var(--wdsColorGray4);
}

.WdsDropdownMenuItem__icon--iconColor {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 18px;
	width: 18px;
	border-radius: 4px;
}
.WdsDropdownMenuItem__action {
	grid-row: 1 / -1;
	grid-column: -1;
	display: flex;
	align-items: center;
}
</style>
