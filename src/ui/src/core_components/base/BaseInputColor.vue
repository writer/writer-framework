<template>
	<input
		ref="pickerEl"
		type="color"
		class="BaseInputColor"
		:value="value"
		:list="datalistId"
		@input="handleInput"
		@change="handleChange"
	/>
	<datalist v-if="datalistId" :id="datalistId">
		<option v-for="color of customColors" :key="color">{{ color }}</option>
	</datalist>
</template>

<script setup lang="ts">
import { PropType, computed, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";

const props = defineProps({
	value: { type: String, required: false, default: undefined },
	customColors: { type: Array as PropType<string[]>, default: () => [] },
});

const emit = defineEmits({
	"update:value": (value: string) => typeof value === "string",
	change: (value: string) => typeof value === "string",
});

const pickerEl = ref<HTMLInputElement | undefined>();

const flattenedInstancePath = inject(injectionKeys.flattenedInstancePath);

const datalistId = computed(() =>
	props.customColors?.length ? `${flattenedInstancePath}_datalist` : null,
);

function handleInput(event: Event) {
	emit("update:value", (event.target as HTMLInputElement).value);
}

function handleChange(event: Event) {
	emit("change", (event.target as HTMLInputElement).value);
}
</script>

<style scoped>
.BaseInputColor {
	width: 12ch;
	border: 0;
	outline: none;
}
</style>
