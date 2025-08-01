import { ref, DeepReadonly, Ref, readonly } from "vue";

function checkIsBindingFormat(val: unknown): boolean {
	return typeof val === "string" && val.startsWith("@{") && val.endsWith("}");
}

type Params = {
	fieldValue: DeepReadonly<Ref<string>>;
	setFieldValue: (value: string) => void;
};

export function useBindingMode({ fieldValue, setFieldValue }: Params) {
	const isBindingMode = ref<boolean>(checkIsBindingFormat(fieldValue.value));

	const lastValues = ref<{
		binding: string;
		noneBinding: string;
	}>({
		binding: checkIsBindingFormat(fieldValue.value) ? fieldValue.value : "",
		noneBinding: isBindingMode.value ? "" : fieldValue.value,
	});

	function toggleBindingMode() {
		if (isBindingMode.value) {
			if (checkIsBindingFormat(fieldValue.value)) {
				lastValues.value.binding = fieldValue.value;
			}

			setFieldValue(lastValues.value.noneBinding);
			isBindingMode.value = false;
		} else {
			lastValues.value.noneBinding = fieldValue.value;

			setFieldValue(lastValues.value.binding);
			isBindingMode.value = true;
		}
	}

	return {
		isBindingMode: readonly(isBindingMode),
		toggleBindingMode,
	};
}
