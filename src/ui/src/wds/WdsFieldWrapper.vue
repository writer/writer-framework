<template>
	<div class="WdsFieldWrapper colorTransformer">
		<template v-if="isExpanded">
			<WdsModal :actions="[OkAction]" :description="hint" :title="label"
				><slot></slot
			></WdsModal>
			<div class="temporaryMissingBar">
				Field <strong>{{ label }}</strong> is open in a new window.
			</div>
		</template>
		<template v-else>
			<div
				v-if="!isExpanded && (label || helpButton)"
				class="WdsFieldWrapper__title"
			>
				<label v-if="label" class="WdsFieldWrapper__title__label"
					>{{ label
					}}<span
						v-if="unit"
						class="WdsFieldWrapper__title__label__unit"
						>&nbsp;:&nbsp;{{ unit }}</span
					>
				</label>
				<WdsButton
					v-if="isExpansible"
					class="WdsFieldWrapper__title__help"
					variant="neutral"
					size="smallIcon"
					data-writer-tooltip="Expand"
					@click="handleExpansion"
				>
					<i class="material-symbols-outlined">open_in_new</i>
				</WdsButton>
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
			<div class="WdsFieldWrapper__slot">
				<slot></slot>
			</div>
			<p v-if="error" class="WdsFieldWrapper__error">{{ error }}</p>
			<p v-if="hint" class="WdsFieldWrapper__hint">{{ hint }}</p>
		</template>
	</div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import WdsButton from "./WdsButton.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";

defineProps({
	label: { type: String, required: false, default: undefined },
	unit: { type: String, required: false, default: undefined },
	hint: { type: String, required: false, default: undefined },
	error: { type: String, required: false, default: undefined },
	isExpansible: { type: Boolean, required: false, default: false },
	helpButton: {
		type: [String, Boolean],
		required: false,
		default: undefined,
	},
});

const emits = defineEmits({
	helpClick: () => true,
	expand: () => true,
	shrink: () => true,
});

const isExpanded = ref(false);

function handleExpansion() {
	emits("expand");
	isExpanded.value = true;
}

const OkAction: ModalAction = {
	desc: "OK",
	fn: () => {
		isExpanded.value = false;
		emits("shrink");
	},
};
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

.temporaryMissingBar {
	background: var(--separatorColor);
	color: var(--secondaryTextColor);
	padding: 16px;
	border-radius: 8px;
}
</style>
