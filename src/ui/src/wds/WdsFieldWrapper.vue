<template>
	<div class="WdsFieldWrapper colorTransformer">
		<div v-if="label || helpButton" class="WdsFieldWrapper__title">
			<label v-if="label" class="WdsFieldWrapper__title__label"
				>{{ label
				}}<span v-if="unit" class="WdsFieldWrapper__title__label__unit"
					>&nbsp;:&nbsp;{{ unit }}</span
				>
			</label>
			<WdsButton
				v-if="helpButton"
				class="WdsFieldWrapper__title__help"
				variant="neutral"
				size="smallIcon"
				:data-writer-tooltip="
					typeof helpButton === 'string' ? helpButton : undefined
				"
				@click="$emit('helpClick')"
			>
				<i class="material-symbols-outlined">help</i>
			</WdsButton>
		</div>
		<div class="WdsFieldWrapper__slot"><slot></slot></div>
		<p v-if="error" class="WdsFieldWrapper__error">{{ error }}</p>
		<p v-if="hint" class="WdsFieldWrapper__hint">{{ hint }}</p>
	</div>
</template>

<script setup lang="ts">
import WdsButton from "./WdsButton.vue";

defineProps({
	label: { type: String, required: false, default: undefined },
	unit: { type: String, required: false, default: undefined },
	hint: { type: String, required: false, default: undefined },
	error: { type: String, required: false, default: undefined },
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

.WdsFieldWrapper__title__label {
	font-size: 14px;
	font-weight: 400;
	line-height: 20px;
}
.WdsFieldWrapper__title__label__unit {
	color: var(--secondaryTextColor);
}

.WdsFieldWrapper__hint,
.WdsFieldWrapper__error {
	margin-top: 4px;
	font-family: Poppins;
	font-size: 12px;
	font-weight: 400;
	line-height: 160%;
}
.WdsFieldWrapper__error:first-letter {
	text-transform: capitalize;
}

.WdsFieldWrapper__hint {
	color: var(--secondaryTextColor);
}

.WdsFieldWrapper__error {
	color: var(--builderErrorColor);
}
</style>
