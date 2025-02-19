<template>
	<BaseInputSliderLayout
		class="BaseInputRangeSlider"
		:min="min"
		:max="max"
		:popover-display-mode="popoverDisplayMode"
		:aria-valuetext="displayValue"
	>
		<div
			ref="slider"
			class="BaseInputRange__slider"
			@mousedown="handleMouseDown"
		>
			<div
				class="BaseInputRange__slider__progress"
				:style="{
					width: `calc(${progress}% + ${thumbRadius}px)`,
					marginLeft: `${progressOffset}%`,
				}"
			></div>
		</div>
		<BaseInputRangeThumb
			v-for="key in [0, 1]"
			:key="key"
			ref="thumbs"
			:value="value[key]"
			:min="min"
			:max="max"
			:step="step"
			:popover-display-mode="popoverDisplayMode"
			:slider-bounding-rect="sliderBoundingRect"
			@update:value="onUpdate(key ? 1 : 0, $event)"
		/>
	</BaseInputSliderLayout>
</template>

<script setup lang="ts">
import { computed, PropType, toRef, useTemplateRef, watch } from "vue";
import BaseInputRangeThumb from "./BaseInputSliderThumb.vue";
import { useBoundingClientRect } from "@/composables/useBoundingClientRect";
import BaseInputSliderLayout from "./BaseInputSliderLayout.vue";
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

const model = defineModel("value", {
	type: Array as PropType<number[]>,
	default: () => [20, 60],
});

function onUpdate(key: 0 | 1, value: number) {
	const copy = [...model.value];
	copy[key] = value;
	model.value = copy.sort((a, b) => a - b);
}

const slider = useTemplateRef("slider");
const thumbs = useTemplateRef("thumbs");

function handleMouseDown(e: MouseEvent) {
	const thumb1 = thumbs.value[0];
	const thumb2 = thumbs.value[1];

	const distance1 = Math.abs(e.x - thumb1.getOffsetLeft());
	const distance2 = Math.abs(e.x - thumb2.getOffsetLeft());

	distance1 > distance2
		? thumb2.handleMouseDown(e)
		: thumb1.handleMouseDown(e);
}

const from = computed(() => Math.min(...model.value));
const to = computed(() => Math.max(...model.value));

const step = toRef(props, "step");
const displayFrom = useNumberFormatByStep(from, step);
const displayTo = useNumberFormatByStep(to, step);
const displayValue = computed(() => `from ${displayFrom} to ${displayTo}`);

const progressOffset = computed(() => {
	if (typeof from.value !== "number") return 50;
	return ((from.value - props.min) / (props.max - props.min)) * 100;
});

const progress = computed(() => {
	if (typeof to.value !== "number") return 50;
	const value = ((to.value - props.min) / (props.max - props.min)) * 100;
	return value - progressOffset.value;
});

const sliderBoundingRect = useBoundingClientRect(slider);

// update the `value` if the `min` or `max` change and `value` is outside of the range
watch(
	() => props.min,
	() => {
		if (!model.value.some((v) => v < props.min)) return;
		model.value = model.value.map((v) => (v < props.min ? props.min : v));
	},
	{ immediate: true },
);
watch(
	() => props.max,
	() => {
		if (!model.value.some((v) => v > props.max)) return;
		model.value = model.value.map((v) => (v > props.max ? props.max : v));
	},
	{ immediate: true },
);
</script>
