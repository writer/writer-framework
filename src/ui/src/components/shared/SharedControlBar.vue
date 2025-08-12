<template>
	<div class="SharedControlBar">
		<div class="SharedControlBar__content">
			<slot></slot>
		</div>

		<div v-if="$slots.actions" class="SharedControlBar__actions">
			<slot name="actions"></slot>
		</div>
	</div>
</template>

<script setup lang="ts"></script>

<style scoped>
.SharedControlBar {
	gap: 8px;
}

.SharedControlBar:has(.SharedControlBar__actions) {
	display: grid;
	grid-template-columns: 1fr auto;
}

.SharedControlBar__actions {
	gap: 8px;
	display: flex;
	flex-direction: column;
}
</style>
