<template>
	<button class="WdsButton colorTransformer" :class="className">
		<slot></slot>
	</button>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";

/** See Variants on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/WDS-Writer-Design-System?node-id=67-701) */
type WdsButtonVariant =
	| "primary"
	| "secondary"
	| "tertiary"
	| "special"
	| "neutral";

/** See Sizes on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/WDS-Writer-Design-System?node-id=67-701) */
type WdsButtonSize = "big" | "small" | "icon" | "smallIcon";

const props = defineProps({
	variant: { type: String as PropType<WdsButtonVariant>, default: "primary" },
	size: { type: String as PropType<WdsButtonSize>, default: "big" },
});

const className = computed(() => [
	"WdsButton",
	`WdsButton--${props.variant}`,
	`WdsButton--${props.size}`,
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
.WdsButton--primary:disabled {
	border-color: #4a46da;
	background-color: #4a46da;
}

/* VARIANTS -- secondary */

.WdsButton--secondary {
	color: var(--buttonTextColor);
	background: #000000;
	border-color: #000000;
}

.WdsButton--secondary:hover,
.WdsButton--secondary:focus {
	border-color: #333333;
	background: #333333;
}
.WdsButton--secondary:disabled {
	border-color: #333333;
	background: #333333;
	opacity: 40%;
}

/* VARIANTS -- tertiary */

.WdsButton--tertiary {
	color: #000000;
	background: #ffffff;
	border-color: #e4e7ed;
}

.WdsButton--tertiary:hover,
.WdsButton--tertiary:focus {
	color: #828282;
}
.WdsButton--tertiary:disabled {
	color: #828282;
	opacity: 50%;
}

/* VARIANTS -- special */

.WdsButton--special {
	color: #5551ff;
	background: #e4e9ff;
	border-color: #e4e9ff;
}

.WdsButton--special:hover,
.WdsButton--special:focus {
	border-color: #bfcbff;
	background: #bfcbff;
}
.WdsButton--special:disabled {
	border-color: #e4e9ff;
	background-color: #e4e9ff;
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

.WdsButton--neutral:disabled {
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
