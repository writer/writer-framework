<script setup lang="ts">
import { WdsColor } from "@/wds/tokens";

defineProps({
	isLast: { type: Boolean, required: false },
});
</script>

<template>
	<div class="BuilderListItem">
		<svg
			viewBox="0 0 17 50"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
			preserveAspectRatio="xMinYMax meet"
			class="BuilderListItem__anchor"
		>
			<path
				d="M1 0 V19 C1 23.4183 4.58172 27 9 27 H17"
				:stroke="WdsColor.Blue2"
			/>
			<path v-if="!isLast" d="M1 19 V54" :stroke="WdsColor.Blue2" />
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
	padding-left: calc(17px + 12px);
}
</style>
