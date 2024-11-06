<template>
	<div class="WdsFieldWrapper colorTransformer">
		<label>{{ label }}</label>
		<div class="slotContainer" :class="{ frameSlot }"><slot></slot></div>
		<div v-if="hint" class="hint">{{ hint }}</div>
	</div>
</template>

<script setup lang="ts">
defineProps<{
	label: string;
	hint?: string;
	frameSlot?: boolean;
}>();
</script>

<style scoped>
@import "@/renderer/colorTransformations.css";

.WdsFieldWrapper {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

label {
	color: var(--primaryTextColor);
	font-size: 14px;
	font-weight: 400;
	line-height: 20px;
}

.slotContainer.frameSlot {
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	border: 1px solid var(--separatorColor);
}

.slotContainer.frameSlot:focus-within {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.hint {
	color: var(--secondaryTextColor);
	margin-top: 4px;
	font-family: Poppins;
	font-size: 12px;
	font-weight: 400;
	line-height: 160%;
}
</style>
