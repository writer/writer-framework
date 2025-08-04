import { ref, Ref, readonly } from "vue";

function checkIsBindingFormat(val: unknown): boolean {
	return typeof val === "string" && val.startsWith("@{") && val.endsWith("}");
}

type Params = {
	fieldViewModel: Ref<string>;
};

export function useBindingMode({ fieldViewModel }: Params) {
	const isBindingMode = ref<boolean>(
		checkIsBindingFormat(fieldViewModel.value),
	);

	const lastValues = ref<{
		binding: string;
		noneBinding: string;
	}>({
		binding: checkIsBindingFormat(fieldViewModel.value)
			? fieldViewModel.value
			: "",
		noneBinding: isBindingMode.value ? "" : fieldViewModel.value,
	});

	function toggleBindingMode() {
		if (isBindingMode.value) {
			if (checkIsBindingFormat(fieldViewModel.value)) {
				lastValues.value.binding = fieldViewModel.value;
			}

			fieldViewModel.value = lastValues.value.noneBinding;
			isBindingMode.value = false;
		} else {
			lastValues.value.noneBinding = fieldViewModel.value;

			fieldViewModel.value = lastValues.value.binding;
			isBindingMode.value = true;
		}
	}

	return {
		isBindingMode: readonly(isBindingMode),
		toggleBindingMode,
	};
}
