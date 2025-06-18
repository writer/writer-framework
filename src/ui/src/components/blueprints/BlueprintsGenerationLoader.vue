<template>
	<div class="BlueprintsGenerationLoader">
		<img
			src="../../assets/logo.svg"
			alt="Writer Framework logo"
			width="72px"
			height="72px"
		/>
		<WdsLoaderDots class="dot-loader" color="black" />
		<p class="rotating-text">
			<span
				v-for="(text, index) in texts"
				:key="index"
				:class="{ active: currentTextIndex === index }"
			>
				{{ text }}
			</span>
		</p>
	</div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from "vue";
import WdsLoaderDots from "@/wds/WdsLoaderDots.vue";

const texts = [
	"Analyzing requirements",
	"Shopping for blocks",
	"Connecting the dots",
	"Wiring the circuits",
	"Flipping the switches",
];
const currentTextIndex = ref(0);

const TEXT_CHANGE_INTERVAL = 4000;

const intervalId = setInterval(() => {
	currentTextIndex.value = (currentTextIndex.value + 1) % texts.length;
}, TEXT_CHANGE_INTERVAL);

onUnmounted(() => clearInterval(intervalId));
</script>

<style scoped>
.BlueprintsGenerationLoader {
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
</style>
