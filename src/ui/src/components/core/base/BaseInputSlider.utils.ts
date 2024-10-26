import { computed, Ref } from "vue";

/**
 * Format a number using `toFixed` according to the number of floating number in the `step`
 */
export function useNumberFormatByStep(
	value: Ref<number | string>,
	step: Ref<number>,
) {
	const precision = computed(
		() => String(step.value).split(".")[1]?.length ?? 0,
	);
	return computed(() => Number(value.value).toFixed(precision.value));
}
