<template>
	<div class="WorkflowsLifeLoading">
		<div class="logoContainer">
			<img src="../../assets/logo.svg" alt="Writer Framework logo" />
			<WdsLoaderDots class="dot-loader" color="black" />
			<div class="rotating-text">
				<span
					v-for="(text, index) in texts"
					:key="index"
					:class="{ active: currentTextIndex === index }"
				>
					{{ text }}
				</span>
			</div>
		</div>
		<div class="background">
			<RotatingCircle custom-class="rotating-circle left" />
			<RotatingCircle custom-class="rotating-circle center" />
			<RotatingCircle custom-class="rotating-circle right" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import WdsLoaderDots from "@/wds/WdsLoaderDots.vue";
import RotatingCircle from "./RotatingCircle.vue";

const texts = [
	"Analyzing requirements",
	"Shopping for blocks",
	"Connecting the dots",
	"Wiring the circuits",
	"Flipping the switches",
];
const currentTextIndex = ref(0);

const TEXT_CHANGE_INTERVAL = 4000;

onMounted(() => {
	setInterval(() => {
		currentTextIndex.value = (currentTextIndex.value + 1) % texts.length;
	}, TEXT_CHANGE_INTERVAL);
});
</script>

<style scoped>
.WorkflowsLifeLoading {
	position: relative;
	height: 306px;
	background: linear-gradient(0deg, #ffd5f8 0.01%, #bfcbff 99.42%);
	overflow: hidden;
	width: 100%;
	border-radius: 8px;
}

.logoContainer {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	z-index: 10;
	min-width: 400px;
}

.dot-loader {
	margin-top: 25px;
	z-index: 10;
}

.background {
	height: 100%;
}

.rotating-text {
	margin-top: 25px;
}

.rotating-text span {
	opacity: 0;
	transition: opacity 0.5s ease-in-out;
	position: absolute;
	left: 50%;
	transform: translateX(-50%);
	text-transform: uppercase;
	font-weight: 500;
	line-height: 160%;
	letter-spacing: 1px;
}

.rotating-text span.active {
	opacity: 1;
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
