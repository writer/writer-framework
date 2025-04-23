<template>
	<button
		class="WdsButton colorTransformer"
		:class="className"
		role="button"
		:style="style"
		:disabled="disabled || loading"
	>
		<div v-if="loading" class="WdsButton__loader">
			<WdsLoaderDots color="white" :size="24" />
		</div>
		<slot></slot>
	</button>
</template>

<script lang="ts">
/** See Variants on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/WDS-Writer-Design-System?node-id=67-701) */
export type WdsButtonVariant =
	| "primary"
	| "secondary"
	| "tertiary"
	| "special"
	| "neutral";

/** See Sizes on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/WDS-Writer-Design-System?node-id=67-701) */
export type WdsButtonSize = "big" | "small" | "icon" | "smallIcon";
</script>

<script setup lang="ts">
import { computed, CSSProperties, defineAsyncComponent, PropType } from "vue";

const WdsLoaderDots = defineAsyncComponent(
	() => import("@/wds/WdsLoaderDots.vue"),
);

const props = defineProps({
	variant: { type: String as PropType<WdsButtonVariant>, default: "primary" },
	size: { type: String as PropType<WdsButtonSize>, default: "big" },
	customSize: { type: String, required: false, default: undefined },
	loading: { type: Boolean, required: false },
	disabled: { type: Boolean, required: false },
});

const style = computed<CSSProperties>(() => {
	if (!props.customSize) return undefined;
	return { width: props.customSize, height: props.customSize };
});

const className = computed(() => [
	"WdsButton",
	`WdsButton--${props.variant}`,
	props.customSize ? undefined : `WdsButton--${props.size}`,
]);
</script>

<style scoped>
@import "@/renderer/colorTransformations.css";

.WdsButton {
	width: fit-content;
	max-width: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	border-radius: 300px;
	font-weight: 600;
	font-size: 0.875rem;
	cursor: pointer;
	box-shadow: var(--buttonShadow);
	outline: none;
	border-style: solid;
	border-width: 1px;
	position: relative;
	overflow: hidden;
}
.WdsButton__loader {
	/* position the loader as absolute to display the loader but keep the original width taken by the content */
	position: absolute;
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: inherit;
}
.WdsButton:disabled {
	cursor: not-allowed;
}

/* VARIANTS */

/* VARIANTS -- primary */

.WdsButton--primary {
	color: var(--buttonTextColor);
	background: var(--buttonColor);
	border-color: var(--buttonColor);
}

.WdsButton--primary:hover,
.WdsButton--primary:focus {
	border-color: var(--intensifiedButtonColor);
	background: var(--intensifiedButtonColor);
}
.WdsButton--primary:disabled,
.WdsButton--primary[aria-disabled="true"] {
	border-color: var(--wdsColorBlue6);
	background-color: var(--wdsColorBlue6);
	opacity: 40%;
}

/* VARIANTS -- secondary */

.WdsButton--secondary {
	color: var(--buttonTextColor);
	background: var(--wdsColorBlack);
	border-color: var(--wdsColorBlack);
}

.WdsButton--secondary:hover,
.WdsButton--secondary:focus {
	border-color: var(--wdsColorGray6);
	background: var(--wdsColorGray6);
}
.WdsButton--secondary:disabled,
.WdsButton--secondary[aria-disabled="true"] {
	border-color: var(--wdsColorGray6);
	background: var(--wdsColorGray6);
	opacity: 40%;
}

/* VARIANTS -- tertiary */

.WdsButton--tertiary {
	color: var(--wdsColorBlack);
	background: var(--wdsColorWhite);
	border-color: var(--wdsColorGray2);
}

.WdsButton--tertiary:hover,
.WdsButton--tertiary:focus {
	color: var(--wdsColorGray4);
}
.WdsButton--tertiary:disabled,
.WdsButton--tertiary[aria-disabled="true"] {
	color: var(--wdsColorGray4);
	opacity: 50%;
}

/* VARIANTS -- special */

.WdsButton--special {
	color: var(--wdsColorBlue5);
	background: var(--wdsColorBlue2);
	border-color: var(--wdsColorBlue2);
}

.WdsButton--special:hover,
.WdsButton--special:focus {
	border-color: var(--wdsColorBlue3);
	background: var(--wdsColorBlue3);
}
.WdsButton--special:disabled,
.WdsButton--special[aria-disabled="true"] {
	border-color: var(--wdsColorBlue2);
	background-color: var(--wdsColorBlue2);
	opacity: 0.4;
}

/* VARIANTS -- neutral (WDS "White" equivalent) */

.WdsButton--neutral {
	border: none;
	box-shadow: none;
	height: fit-content;
	background: unset;
	margin: 0;
	padding: 0;
}

.WdsButton--neutral:focus,
.WdsButton--neutral:hover {
	color: unset;
	border: none;
	box-shadow: none;
	background: var(--builderSubtleSeparatorColor);
}

.WdsButton--neutral:disabled,
.WdsButton--neutral[aria-disabled="true"] {
	opacity: 0.4;
}

/* SIZES */

.WdsButton--big {
	padding: 10px 20px 10px 20px;
}

.WdsButton--small {
	height: 32px;
	padding: 4px 16px 4px 16px;
}

.WdsButton--icon {
	height: 40px;
	width: 40px;
}

.WdsButton--smallIcon {
	height: 32px;
	width: 32px;
}
</style>
