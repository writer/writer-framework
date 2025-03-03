<template>
	<div class="WdsLoaderDots" :style="{ '--dotSize': '6px' }">
		<span class="WdsLoaderDots__dot"></span>
		<span class="WdsLoaderDots__dot"></span>
		<span class="WdsLoaderDots__dot"></span>
	</div>
</template>

<style scoped>
.WdsLoaderDots {
	width: 100px;
	height: 100%;
	display: flex;
	gap: var(--dotSize);
	align-items: center;
	justify-content: center;
}

.WdsLoaderDots__dot {
	display: inline-block;
	width: var(--dotSize);
	height: var(--dotSize);
	position: relative;
}

.WdsLoaderDots__dot::after {
	display: inline-block;
	content: "";
	position: absolute;
	background-color: currentColor;
	width: calc(var(--dotSize) / 2);
	height: calc(var(--dotSize) / 2);
	border-radius: 50%;
	animation: changeSize 1.5s infinite;

	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
}

.WdsLoaderDots__dot:nth-child(1)::after {
	animation-delay: 0s;
}
.WdsLoaderDots__dot:nth-child(2)::after {
	animation-delay: 0.5s;
}
.WdsLoaderDots__dot:nth-child(3)::after {
	animation-delay: 1s;
}

@keyframes changeSize {
	0% {
		width: calc(var(--dotSize) / 2);
		height: calc(var(--dotSize) / 2);
	}
	50% {
		width: var(--dotSize);
		height: var(--dotSize);
	}
	100% {
		width: calc(var(--dotSize) / 2);
		height: calc(var(--dotSize) / 2);
	}
}
</style>
