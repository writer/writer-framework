<template>
	<div class="BuilderAsyncLoader">
		<LoadingSymbol />
	</div>
</template>

<script setup lang="ts">
import LoadingSymbol from "@/renderer/LoadingSymbol.vue";
</script>

<style scoped>
.BuilderAsyncLoader {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
}
</style>
