<script lang="ts">
/** See Variants on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/.WDS-Writer-Design-System?node-id=8523-6185&t=wftDc1qTFGQKX8rM-4) */
export type WdsButtonSplitVariant =
	| "primary"
	| "secondary"
	| "tertiary"
	| "special";

export type WdsButtonSplitSize = "default" | "small";
</script>

<script setup lang="ts">
import BaseTransitionSlideFade from "@/components/core/base/BaseTransitionSlideFade.vue";
import { useFloating, offset } from "@floating-ui/vue";
import { computed, PropType, ref, useTemplateRef } from "vue";

const props = defineProps({
	variant: {
		type: String as PropType<WdsButtonSplitVariant>,
		default: "primary",
	},
	size: { type: String as PropType<WdsButtonSplitSize>, default: "default" },
	disabled: { type: Boolean, required: false },
});

const classNames = computed(() => [
	`WdsButtonSplit--size-${props.size}`,
	`WdsButtonSplit--variant-${props.variant}`,
	props.disabled ? `WdsButtonSplit--disabled` : undefined,
]);

const emits = defineEmits({
	mainClick: () => true,
	dropdownOpen: () => true,
	dropdownClose: () => true,
});

const btn = useTemplateRef("btn");
const dropdown = useTemplateRef("dropdown");

const isDropdownOpen = ref(false);

const { floatingStyles } = useFloating(btn, dropdown, {
	placement: "bottom-end",
	middleware: [offset(12)],
});

function toggleDropdown(value = !isDropdownOpen.value) {
	isDropdownOpen.value = value;
	isDropdownOpen.value ? emits("dropdownOpen") : emits("dropdownClose");
}

defineExpose({ toggleDropdown });
</script>

<template>
	<div ref="btn" class="WdsButtonSplit" :class="classNames">
		<button
			type="button"
			class="WdsButtonSplit__main"
			:disabled="disabled"
			@click="$emit('mainClick')"
		>
			<slot name="button" />
		</button>
		<hr class="WdsButtonSplit__divider" />
		<button
			class="WdsButtonSplit__dropdownTrigger"
			type="button"
			:disabled="disabled"
			@click.capture="toggleDropdown()"
		>
			<i class="material-symbols-outlined">{{
				isDropdownOpen ? "keyboard_arrow_up" : "keyboard_arrow_down"
			}}</i>
		</button>
		<BaseTransitionSlideFade>
			<div v-if="isDropdownOpen" ref="dropdown" :style="floatingStyles">
				<slot name="dropdown" />
			</div>
		</BaseTransitionSlideFade>
	</div>
</template>

<style lang="css" scoped>
.WdsButtonSplit {
	position: relative;
	display: flex;
	border-radius: 300px;
	box-shadow: var(--buttonShadow);
	border: 1px solid transparent;
	align-items: center;
	height: 40px;
	gap: 8px;
	padding-left: 12px;
	padding-right: 12px;
}

.WdsButtonSplit--disabled {
	opacity: 40%;
}
.WdsButtonSplit--disabled .WdsButtonSplit__dropdownTrigger,
.WdsButtonSplit--disabled .WdsButtonSplit__main {
	cursor: not-allowed;
}

.WdsButtonSplit__dropdownTrigger,
.WdsButtonSplit__main {
	background-color: transparent;
	border: none;
	cursor: pointer;
}

.WdsButtonSplit__main {
	display: flex;
	align-items: center;
	justify-content: flex-start;
	gap: 8px;
	font-weight: 600;
}
.WdsButtonSplit__dropdownTrigger {
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20px;
	border-radius: 50%;
	height: 20px;
	width: 20px;
}
.WdsButtonSplit__divider {
	display: block;
	width: 1px;
	height: 100%;
	border: none;
	height: 24px;
}

/* variant - primary */

.WdsButtonSplit--variant-primary .WdsButtonSplit__divider {
	background: var(--wdsColorBlue4);
}
.WdsButtonSplit--variant-primary,
.WdsButtonSplit--variant-primary .WdsButtonSplit__dropdownTrigger {
	color: var(--wdsColorWhite);
	background: var(--wdsColorBlue5);
}
.WdsButtonSplit--variant-primary:not(.WdsButtonSplit--disabled):hover,
.WdsButtonSplit--variant-primary:not(.WdsButtonSplit--disabled)
	.WdsButtonSplit__dropdownTrigger:hover {
	background: var(--wdsColorBlue6);
}

/* variant - secondary */

.WdsButtonSplit--variant-secondary .WdsButtonSplit__divider {
	background: var(--wdsColorGray5);
}
.WdsButtonSplit--variant-secondary,
.WdsButtonSplit--variant-secondary .WdsButtonSplit__dropdownTrigger {
	color: var(--wdsColorWhite);
	background: var(--wdsColorBlack);
}
.WdsButtonSplit--variant-secondary:not(.WdsButtonSplit--disabled):hover,
.WdsButtonSplit--variant-secondary:not(.WdsButtonSplit--disabled)
	.WdsButtonSplit__dropdownTrigger:hover {
	background: var(--wdsColorGray6);
}

/* variant - tertiary */

.WdsButtonSplit--variant-tertiary .WdsButtonSplit__divider {
	background: var(--wdsColorGray2);
}
.WdsButtonSplit--variant-tertiary,
.WdsButtonSplit--variant-tertiary .WdsButtonSplit__dropdownTrigger {
	color: var(--wdsColorBlack);
	background: var(--wdsColorWhite);
}
.WdsButtonSplit--variant-tertiary:not(.WdsButtonSplit--disabled):hover,
.WdsButtonSplit--variant-tertiary:not(.WdsButtonSplit--disabled)
	.WdsButtonSplit__dropdownTrigger:hover {
	color: var(--wdsColorGray4);
}

/* variant - special */

.WdsButtonSplit--variant-special .WdsButtonSplit__divider {
	background: var(--wdsColorBlue5);
}
.WdsButtonSplit--variant-special,
.WdsButtonSplit--variant-special .WdsButtonSplit__dropdownTrigger {
	color: var(--wdsColorBlue5);
	background: var(--wdsColorBlue2);
}
.WdsButtonSplit--variant-special:not(.WdsButtonSplit--disabled):hover,
.WdsButtonSplit--variant-special:not(.WdsButtonSplit--disabled)
	.WdsButtonSplit__dropdownTrigger:hover {
	background: var(--wdsColorBlue3);
}

/* size */

.WdsButtonSplit--size-default .WdsButtonSplit__main {
	font-size: 14px;
}

.WdsButtonSplit--size-small .WdsButtonSplit__main {
	font-size: 12px;
}
</style>
