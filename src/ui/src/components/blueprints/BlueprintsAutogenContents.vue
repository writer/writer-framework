<template>
	<div class="BlueprintsAutogenContents">
		<div class="BlueprintsAutogenContents__contents">
			<slot></slot>
		</div>
		<div
			class="BlueprintsAutogenContents__background"
			:class="{ busy: isBusy }"
		>
			<GradientCircle class="rotating-circle left" />
			<GradientCircle class="rotating-circle center" />
			<GradientCircle class="rotating-circle right" />
		</div>
	</div>
</template>

<script setup lang="ts">
import GradientCircle from "./GradientCircle.vue";

defineProps({
	isBusy: { type: Boolean, required: true },
});
</script>

<style scoped>
.BlueprintsAutogenContents {
	position: relative;
	height: 306px;
	overflow: hidden;
	width: 100%;
	border-radius: 8px;
}

.BlueprintsAutogenContents__contents {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	position: absolute;
	padding: 40px;
	z-index: 10;
	width: 100%;
	height: 100%;
}

.BlueprintsAutogenContents__background {
	position: "absolute";
	inset: 0;
	background: linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%);
	opacity: 50%;
}

.BlueprintsAutogenContents__background.busy {
	opacity: 100%;
}

@keyframes rotateCounterClockwise {
	from {
		transform: rotate(45deg);
	}

	to {
		transform: rotate(-315deg);
	}
}

@keyframes rotateClockwise {
	from {
		transform: rotate(-45deg);
	}

	to {
		transform: rotate(315deg);
	}
}

.rotating-circle {
	transform-origin: center;
	position: absolute;
}

.rotating-circle.left {
	animation: rotateCounterClockwise 12s linear infinite;
	top: -50%;
	left: -30%;
	z-index: 1;
}

.rotating-circle.center {
	animation: rotateClockwise 16s linear infinite;
	top: -50%;
	left: 17%;
	z-index: 2;
}

.rotating-circle.right {
	animation: rotateClockwise 20s linear infinite;
	top: -50%;
	right: -30%;
	z-index: 3;
}
</style>
