<template>
	<WdsTextInput
		v-model="model"
		class="WdsPasswordInput"
		:type="type"
		:right-icon="revealable ? rightIcon : undefined"
		:autofocus="autofocus"
		:invalid="invalid"
		:variant="variant"
		@right-icon-click="revealable ? (isShown = !isShown) : undefined"
	/>
</template>

<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import WdsTextInput from "./WdsTextInput.vue";

const model = defineModel({ type: String });

defineProps({
	invalid: { type: Boolean, required: false },
	revealable: { type: Boolean, default: true, required: false },
	variant: { type: String as PropType<"ghost">, default: undefined },
	rightText: { type: String, required: false, default: "" },
	autofocus: { type: Boolean },
});

const isShown = ref(false);

const rightIcon = computed(() =>
	isShown.value ? "visibility_off" : "visibility",
);
const type = computed(() => (isShown.value ? "text" : "password"));
</script>
