import { computed, Ref } from "vue";

export function useDateTimeFormatter(
	date: Ref<Date>,
	options: {
		dateOptions?: Intl.DateTimeFormatOptions;
		timeOptions?: Intl.DateTimeFormatOptions;
	} = {
		dateOptions: {
			year: "numeric",
			month: "short",
			day: "numeric",
		},
		timeOptions: {
			hour: "numeric",
			minute: "2-digit",
			second: "2-digit",
			hour12: true,
		},
	},
) {
	const { dateOptions, timeOptions } = options;

	const formattedDate = computed(() =>
		date.value.toLocaleDateString(undefined, dateOptions),
	);

	const formattedTime = computed(() =>
		date.value.toLocaleTimeString(undefined, timeOptions),
	);

	return {
		formattedDate,
		formattedTime,
	};
}
