<script setup lang="ts"></script>

<template>
	<div class="WdsSkeletonLoader" aria-busy="true"></div>
</template>

<style lang="css" scoped>
.WdsSkeletonLoader {
	width: 100%;
	height: 12px;
	background-color: var(--wdsColorGray2);
	border-radius: 8px;
	background: linear-gradient(
		90deg,
		var(--wdsColorGray0) 0%,
		var(--wdsColorGray2) 50%,
		var(--wdsColorGray0) 100%
	);
	background-size: 200% 100%;
	animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
	0% {
		background-position: 100% 0;
	}
	100% {
		background-position: -100% 0;
	}
}
</style>
