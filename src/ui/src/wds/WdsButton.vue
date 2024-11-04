<template>
	<button class="WdsButton colorTransformer" :class="className">
		<slot></slot>
	</button>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";

/** See Variants on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/WDS-Writer-Design-System?node-id=67-701) */
type WdsButtonVariant = "primary" | "secondary" | "tertiary" | "neutral";

/** See Sizes on [Figma](https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/WDS-Writer-Design-System?node-id=67-701) */
type WdsButtonSize = "big" | "small" | "unpadded";

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
	gap: 8px;
	border-radius: 300px;
	font-weight: 600;
	line-height: 20px;
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

/* VARIANTS -- neutral */

.WdsButton--neutral {
	border: none;
	box-shadow: none;
	background: unset;
	margin: 0;
	padding: 0;
}

.WdsButton--neutral:hover,
.WdsButton--neutral:focus {
	color: unset;
	border: none;
	box-shadow: none;
	background: unset;
}

.WdsButton--neutral:disabled {
	color: #828282;
	opacity: 50%;
}

/* SIZES */

.WdsButton--big {
	padding: 10px 20px 10px 20px;
}

.WdsButton--small {
	height: 32px;
	padding: 10px 16px 10px 16px;
}

.WdsButton--unpadded {
	padding: 0;
}
</style>
