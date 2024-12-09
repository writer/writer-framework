import { computed, ComputedRef } from "vue";

export function usePercentageFormatter(
	number: ComputedRef<number>,
	options: Pick<
		Intl.NumberFormatOptions,
		"minimumFractionDigits" | "maximumFractionDigits"
	> = {
		minimumFractionDigits: 0,
		maximumFractionDigits: 1,
	},
) {
	const formatter = new Intl.NumberFormat(undefined, {
		style: "percent",
		...options,
	});
	return computed(() => formatter.format(number.value));
}
