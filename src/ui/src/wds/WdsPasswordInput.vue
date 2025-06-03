<template>
	<WdsTextInput
		v-model="model"
		class="WdsPasswordInput"
		:type="type"
		:right-icon="rightIcon"
		:autofocus="autofocus"
		:invalid="invalid"
		:variant="variant"
		@right-icon-click="isShown = !isShown"
	/>
</template>

<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import WdsTextInput from "./WdsTextInput.vue";

const model = defineModel({ type: String });

defineProps({
	invalid: { type: Boolean, required: false },
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
