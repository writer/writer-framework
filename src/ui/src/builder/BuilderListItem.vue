<script setup lang="ts">
import { WdsColor } from "@/wds/tokens";
import { computed } from "vue";

const props = defineProps({
	isLast: { type: Boolean, required: false },
	height: { type: Number, required: false, default: 1_000 },
	color: { type: String, required: false, default: WdsColor.Blue2 },
	colorLast: { type: String, required: false, default: WdsColor.Blue2 },
});

const midHeight = computed(() => props.height / 2);
const viewBox = computed(() => `0 0 17 ${props.height}`);

const d1 = computed(() =>
	[
		"M1 0",
		`V${midHeight.value - 8}`,
		`C1 ${midHeight.value - 4}.4183 4.58172 ${midHeight.value} 9 ${midHeight.value}`,
		`H17`,
	].join(" "),
);

const d2 = computed(() =>
	[`M1 ${midHeight.value - 8}`, `V${props.height}`].join(" "),
);
</script>

<template>
	<div class="BuilderListItem">
		<svg
			:viewBox="viewBox"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
			preserveAspectRatio="xMinYMax meet"
			class="BuilderListItem__anchor"
		>
			<path v-if="!isLast" :d="d2" :stroke="colorLast" stroke-width="1" />
			<path :d="d1" :stroke="color" stroke-width="1" />
		</svg>
		<div class="BuilderListItem__content">
			<slot />
		</div>
	</div>
</template>

<style scoped>
.BuilderListItem {
	align-items: stretch;
	column-gap: 12px;
	position: relative;
	overflow: hidden;
}
.BuilderListItem__anchor {
	min-width: 17px;
	max-width: 17px;
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	margin: auto 0;
}
.BuilderListItem__content {
	width: 100%;
	padding-left: 17px;
}
</style>
