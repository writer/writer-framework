<template>
	<button
		class="WdsButtonLink"
		:disabled="disabled"
		:class="className"
		type="button"
	>
		<WdsIcon v-if="leftIcon" :name="leftIcon" />
		<span class="WdsButtonLink__text">{{ text }}</span>
		<WdsIcon v-if="rightIcon" :name="rightIcon" />
	</button>
</template>

<script lang="ts">
export type WdsButtonLinkWeight = "default" | "semibold";
export type WdsButtonLinkVariant = "primary" | "secondary";
</script>

<script setup lang="ts">
import { computed, PropType } from "vue";
import WdsIcon from "./WdsIcon.vue";

const props = defineProps({
	variant: {
		type: String as PropType<WdsButtonLinkVariant>,
		default: "primary",
	},
	weight: {
		type: String as PropType<WdsButtonLinkWeight>,
		default: "default",
	},
	leftIcon: { type: String, required: false, default: undefined },
	rightIcon: { type: String, required: false, default: undefined },
	text: { type: String, required: true },
	disabled: { type: Boolean },
});
const className = computed(() => [
	`WdsButtonLink--variant-${props.variant}`,
	`WdsButtonLink--weight-${props.weight}`,
]);
</script>

<style scoped>
.WdsButtonLink {
	background-color: transparent;
	border: none;
	text-align: left;
	display: flex;
	align-items: center;
	gap: 4px;

	cursor: pointer;
}
.WdsButtonLink:disabled {
	cursor: not-allowed;
	opacity: 40%;
}

.WdsButtonLink__text {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
	display: block;
}

.WdsButtonLink:hover .WdsButtonLink__text {
	text-decoration: underline;
}

.WdsButtonLink--variant-primary {
	color: var(--wdsColorBlue5);
}
.WdsButtonLink--variant-secondary {
	color: var(--wdsColorBlack);
}

.WdsButtonLink--weight-default {
	font-weight: 400;
}
.WdsButtonLink--weight-semibold {
	font-weight: 500;
}
</style>
