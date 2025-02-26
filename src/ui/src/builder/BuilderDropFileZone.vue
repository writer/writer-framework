<template>
	<div class="BuilderDropFileZone">
		<img
			src="@/assets/file-drop-placeholder.svg"
			alt="Drop file illustration"
		/>
		<h2>Upload files</h2>
		<p>Files can be up to {{ SOURCE_FILE_MAX_SIZE_MB }}mb</p>
	</div>
</template>

<script setup lang="ts">
import { SOURCE_FILE_MAX_SIZE_MB } from "@/core/useSourceFiles";
</script>

<style scoped>
.BuilderDropFileZone {
	background-color: var(--wdsColorBlue1);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 100%;
	width: 100%;
	pointer-events: none;
}

.BuilderDropFileZone img {
	height: 160px;
	margin-bottom: 20px;
	font-size: 24px;
	font-weight: 500;
}

.BuilderDropFileZone img {
	height: 160px;
	margin-bottom: 8px;
	font-size: 12px;
}
</style>
