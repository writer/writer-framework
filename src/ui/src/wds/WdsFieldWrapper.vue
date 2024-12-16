<template>
	<div class="WdsFieldWrapper colorTransformer">
		<div v-if="label || helpButton" class="WdsFieldWrapper__title">
			<label v-if="label" class="WdsFieldWrapper__title__label"
				>{{ label
				}}<span v-if="unit" class="WdsFieldWrapper__title__label__unit"
					>&nbsp;:&nbsp;{{ unit }}</span
				>
			</label>
			<button
				v-if="helpButton"
				class="WdsFieldWrapper__title__help"
				variant="subtle"
				:title="typeof helpButton === 'string' ? helpButton : undefined"
				@click="$emit('helpClick')"
			>
				<i class="material-symbols-outlined">help</i>
			</button>
		</div>
		<div class="WdsFieldWrapper__slot"><slot></slot></div>
		<div v-if="hint" class="WdsFieldWrapper__hint">{{ hint }}</div>
	</div>
</template>

<script setup lang="ts">
defineProps({
	label: { type: String, required: false, default: undefined },
	unit: { type: String, required: false, default: undefined },
	hint: { type: String, required: false, default: undefined },
	helpButton: {
		type: [String, Boolean],
		required: false,
		default: undefined,
	},
});

defineEmits({
	helpClick: () => true,
});
</script>

<style scoped>
@import "@/renderer/colorTransformations.css";

.WdsFieldWrapper {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.WdsFieldWrapper__title {
	color: var(--primaryTextColor);
	display: grid;
	grid-template-columns: 1fr auto;
	align-items: center;
	flex-wrap: wrap;
	gap: 8px;
}

.WdsFieldWrapper__title__help {
	background-color: transparent;
	border: none;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
}
.WdsFieldWrapper__title__help:hover {
	color: var(--primaryColor);
}

.WdsFieldWrapper__title__label {
	font-size: 14px;
	font-weight: 400;
	line-height: 20px;
}
.WdsFieldWrapper__title__label__unit {
	color: var(--secondaryTextColor);
}

.WdsFieldWrapper__hint {
	color: var(--secondaryTextColor);
	margin-top: 4px;
	font-family: Poppins;
	font-size: 12px;
	font-weight: 400;
	line-height: 160%;
}
</style>
