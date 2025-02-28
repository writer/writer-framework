<template>
	<div class="WdsToast" :class="`WdsToast--${type}`">
		<div class="WdsToast__icon">
			<span class="material-symbols-outlined">{{ icon }}</span>
		</div>
		<p>{{ message }}</p>
		<button v-if="action" class="WdsToast__action" @click="action.func">
			{{ action.label }}
			<span class="material-symbols-outlined">{{ action.icon }}</span>
		</button>
		<WdsButton
			v-if="closable"
			class="WdsToast__close"
			variant="neutral"
			size="smallIcon"
			@click="$emit('close')"
		>
			<span class="material-symbols-outlined">close</span>
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";
import WdsButton from "./WdsButton.vue";
import type { Toast, ToastAction } from "@/builder/useToast";

const props = defineProps({
	type: { type: String as PropType<Toast["type"]>, required: true },
	message: { type: String, required: true },
	closable: { type: Boolean },
	action: {
		type: Object as PropType<ToastAction>,
		required: false,
		default: undefined,
	},
});

defineEmits({
	close: () => true,
});

const icon = computed(() => {
	switch (props.type) {
		case "info":
			return "info";
		case "success":
			return "check";
		case "error":
			return "close";
		default:
			return "question_mark";
	}
});
</script>

<style scoped>
.WdsToast {
	height: 48px;
	padding: 10px 12px;

	display: flex;
	align-items: center;
	gap: 12px;

	background-color: var(--wdsColorBlack);
	color: var(--wdsColorWhite);
	border-radius: 4px;
	box-shadow: var(--wdsShadowMenu);
}

.WdsToast__icon {
	height: 18px;
	width: 18px;
	border-radius: 50%;
	color: var(--wdsColorBlack);

	display: flex;
	align-items: center;
	justify-content: center;

	background-color: var(--wdsColorGreen3);
}

.WdsToast__action {
	background-color: transparent;
	border: none;
	display: flex;
	gap: 4px;
	font-weight: 500;
}
.WdsToast__action:hover {
	text-decoration: underline;
}

.WdsToast--success .WdsToast__icon {
	background-color: var(--wdsColorGreen3);
}
.WdsToast--error .WdsToast__icon {
	background-color: var(--wdsColorOrange5);
}
.WdsToast--info .WdsToast__icon {
	background-color: var(--wdsColorBlue2);
}

.WdsToast__close:hover,
.WdsToast__close:focus {
	color: var(--wdsColorBlack);
}
</style>
