<script lang="ts">
export type WdsStateDotState = "error" | "deployed" | "newDraft" | "draft";
</script>

<script setup lang="ts">
import { PropType } from "vue";

defineProps({
	state: { type: String as PropType<WdsStateDotState>, required: true },
});
</script>

<template>
	<div class="WdsStateDotState" :class="`WdsStateDotState--${state}`"></div>
</template>

<style scoped>
.WdsStateDotState {
	height: 16px;
	min-height: 16px;
	width: 16px;
	min-width: 16px;
	border-radius: 50%;
}
.WdsStateDotState::after {
	content: "";
	display: block;
	height: 8px;
	width: 8px;
	border-radius: 50%;
	position: relative;
	top: 4px;
	left: 4px;
}

/* error */
.WdsStateDotState--error {
	background-color: var(--wdsColorOrange2);
}
.WdsStateDotState--error::after {
	background-color: var(--wdsColorOrange5);
}
/* deployed */
.WdsStateDotState--deployed {
	background-color: var(--wdsColorGreen3);
}
.WdsStateDotState--deployed::after {
	background-color: var(--wdsColorGreen5);
}
/* newDraft */
.WdsStateDotState--newDraft {
	background-color: var(--wdsColorBlue2);
}
.WdsStateDotState--newDraft::after {
	background-color: var(--wdsColorBlue4);
}
/* draft */
.WdsStateDotState--draft {
	background-color: var(--wdsColorGray3);
}
.WdsStateDotState--draft::after {
	background-color: var(--wdsColorWhite);
}
</style>
