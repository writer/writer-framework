<template>
	<BaseInputSliderLayout
		:min="min"
		:max="max"
		:popover-display-mode="popoverDisplayMode"
		:aria-valuenow="value"
		:aria-valuetext="`${displayValue} (${Math.round(progress)}%)`"
	>
		<div
			ref="slider"
			class="BaseInputRange__slider"
			@mousedown="thumb.handleMouseDown"
		>
			<div
				class="BaseInputRange__slider__progress"
				:style="{ width: `calc(${progress}% + ${thumbRadius}px)` }"
			></div>
		</div>
		<BaseInputRangeThumb
			ref="thumb"
			:value="value"
			:min="min"
			:max="max"
			:step="step"
			:popover-display-mode="popoverDisplayMode"
			:slider-bounding-rect="sliderBoundingRect"
			@update:value="model = $event"
		/>
	</BaseInputSliderLayout>
</template>

<script setup lang="ts">
import { computed, PropType, toRef, watch, useTemplateRef } from "vue";
import BaseInputRangeThumb from "./BaseInputSliderThumb.vue";
import BaseInputSliderLayout from "./BaseInputSliderLayout.vue";
import { useBoundingClientRect } from "@/composables/useBoundingClientRect";
import { useNumberFormatByStep } from "./BaseInputSlider.utils";

const thumbRadius = 9;

const props = defineProps({
	min: { type: Number, default: 0 },
	max: { type: Number, default: 100 },
	step: { type: Number, default: 1 },
	popoverDisplayMode: {
		type: String as PropType<"always" | "onChange">,
		default: "onChange",
	},
});

const model = defineModel("value", { type: Number, default: 50 });

const slider = useTemplateRef("slider");
const thumb = useTemplateRef("thumb");

const displayValue = useNumberFormatByStep(model, toRef(props, "step"));

const progress = computed(() => {
	if (typeof model.value !== "number") return 50;
	return ((model.value - props.min) / (props.max - props.min)) * 100;
});

const sliderBoundingRect = useBoundingClientRect(slider);

// update the `value` if the `min` or `max` change and `value` is outside of the range
watch(
	() => props.min,
	() => {
		if (typeof model.value === "number" && model.value < props.min)
			model.value = props.min;
	},
	{ immediate: true },
);
watch(
	() => props.max,
	() => {
		if (typeof model.value === "number" && model.value > props.max)
			model.value = props.max;
	},
	{ immediate: true },
);
</script>
