<script setup lang="ts">
import { WdsColor } from "@/wds/tokens";

defineProps({
	isLast: { type: Boolean, required: true },
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
		<slot />
	</div>
</template>

<style scoped>
.BuilderListItem {
	display: grid;
	grid-template-columns: auto 1fr;
	align-items: center;
	column-gap: 12px;
}
.BuilderListItem__anchor {
	min-width: 17px;
	height: fit-content;
}
.BuilderListItem__content {
	/* height: 100px; */
}
</style>
