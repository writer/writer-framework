<script setup lang="ts">
import { WdsColor } from "./tokens";

defineProps({
	color: { type: String, required: false, default: WdsColor.Blue5 },
});
</script>

<template>
	<svg
		width="16"
		height="16"
		viewBox="0 0 16 16"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
	>
		<circle cx="4" cy="8" :fill="color">
			<animate
				attributeName="r"
				values="0.5;3;0"
				dur="1.2s"
				repeatCount="indefinite"
			/>
		</circle>
		<circle cx="8" cy="8" :fill="color">
			<animate
				attributeName="r"
				values="0.5;3;0"
				dur="1.2s"
				begin="0.4s"
				repeatCount="indefinite"
			/>
		</circle>
		<circle cx="12" cy="8" :fill="color">
			<animate
				attributeName="r"
				values="0.5;3;0"
				dur="1.2s"
				begin="0.8s"
				repeatCount="indefinite"
			/>
		</circle>
	</svg>
</template>
