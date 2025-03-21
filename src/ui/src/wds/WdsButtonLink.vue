<template>
	<button
		class="WdsButtonLink"
		:disabled="disbaled"
		:class="className"
		role="button"
	>
		<i v-if="leftIcon" class="material-symbols-outlined">{{ leftIcon }}</i>
		<span class="WdsButtonLink__text">{{ text }}</span>
		<i v-if="rightIcon" class="material-symbols-outlined">{{
			rightIcon
		}}</i>
	</button>
</template>

<script lang="ts">
export type WdsButtonLinkWeight = "default" | "semibold";
export type WdsButtonLinkVariant = "primary" | "secondary";
</script>

<script setup lang="ts">
import { computed, PropType } from "vue";

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
	disbaled: { type: Boolean },
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
</style>
