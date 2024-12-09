import { ComputedRef, computed } from "vue";

type Fields = Record<string, ComputedRef<unknown>>;

export function useFieldValueAsYesNo(
	fields: Fields,
	key: string,
): ComputedRef<boolean> {
	return computed(() => fields[key].value === "yes");
}
