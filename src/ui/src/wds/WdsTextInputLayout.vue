<template>
	<div
		class="WdsTextInputLayout"
		:class="{ 'WdsTextInputLayout--ghost': variant === 'ghost' }"
		v-bind="$attrs"
		:aria-invalid="invalid"
		:style="{
			gridTemplateColumns: gridTemplateColumns,
		}"
	>
		<WdsIcon v-if="leftIcon" :name="leftIcon" />
		<slot />
		<p v-if="rightText" class="WdsTextInputLayout__rightText">
			{{ rightText }}
		</p>
		<button
			v-if="rightIcon"
			class="WdsTextInputLayout__rightIcon"
			type="button"
			@click="$emit('rightIconClick')"
		>
			<WdsIcon :name="rightIcon" />
		</button>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";
import WdsIcon from "./WdsIcon.vue";

const props = defineProps({
	leftIcon: { type: String, required: false, default: undefined },
	rightIcon: { type: String, required: false, default: undefined },
	invalid: { type: Boolean, required: false },
	variant: { type: String as PropType<"ghost">, default: undefined },
	rightText: { type: String, required: false, default: "" },
});

defineEmits({
	rightIconClick: () => true,
});

const gridTemplateColumns = computed(() =>
	[
		props.leftIcon ? "auto" : undefined,
		"minmax(0, 1fr)",
		props.rightText ? "auto" : undefined,
		props.rightIcon ? "auto" : undefined,
	]
		.filter(Boolean)
		.join(" "),
);
</script>

<style scoped>
@import "@/renderer/colorTransformations.css";

.WdsTextInputLayout {
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

.WdsTextInputLayout:focus,
.WdsTextInputLayout:focus-within {
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.WdsTextInputLayout--ghost {
	border-color: transparent;
	background-color: transparent;
	transition:
		box-shadow,
		background-color,
		border-color ease-in-out 0.2s;
}
.WdsTextInputLayout--ghost:disabled {
	cursor: not-allowed;
}
.WdsTextInputLayout--ghost:not(:disabled):hover {
	background-color: transparent;
	border-color: var(--wdsColorBlue3);
}
.WdsTextInputLayout--ghost:not(:disabled):focus,
.WdsTextInputLayout--ghost:not(:disabled):focus-within {
	background-color: transparent;
}

.WdsTextInputLayout {
	cursor: pointer;
	display: grid;
	align-items: center;
	gap: 8px;
}

.WdsTextInputLayout i {
	color: var(--wdsColorGray5);
}

.WdsTextInputLayout__rightIcon {
	border: none;
	background-color: transparent;
	display: flex;
	align-items: center;
	cursor: pointer;
}

.WdsTextInputLayout__rightText {
	padding-left: 8px;
	border-left: 2px solid var(--separatorColor);
}

.WdsTextInputLayout[aria-invalid="true"] {
	border-color: var(--wdsColorOrange5);
}
</style>
