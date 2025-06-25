<script lang="ts">
export type WdsStateDotState = "error" | "deployed" | "newDraft" | "draft";
</script>

<script setup lang="ts">
import { PropType, watch, ref } from "vue";
import WdsModal from "@/wds/WdsModal.vue";

const props = defineProps({
	state: { type: String as PropType<WdsStateDotState>, required: true },
});

let modalTimer: ReturnType<typeof setTimeout>;
const isModalShown = ref(false);

watch(
	() => props.state,
	(newState) => {
		if (newState !== "error") {
			isModalShown.value = false;
			clearTimeout(modalTimer);
			return;
		}
		modalTimer = setTimeout(() => {
			isModalShown.value = true;
		}, 1000);
	},
);
</script>

<template>
	<div class="WdsStateDotState" :class="`WdsStateDotState--${state}`">
		<div v-if="state == 'error'" class="WdsStateDotState--cover">
			<WdsModal
				v-if="isModalShown"
				title="We’re trying to reconnect..."
				size="normal"
			>
				<p>
					Connection was lost due to a network issue or an ongoing
					update. Please hang tight!
				</p>
			</WdsModal>
		</div>
	</div>
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

.WdsStateDotState--cover {
	position: absolute;
	top: 0;
	left: 0;
	height: 100vh;
	width: 100vw;
	background: rgba(255, 255, 255, 0.5);
}
</style>
