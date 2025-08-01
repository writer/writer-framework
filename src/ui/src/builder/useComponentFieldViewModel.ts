import { computed, inject, Ref, DeepReadonly } from "vue";
import injectionKeys from "@/injectionKeys";
import { useComponentActions } from "./useComponentActions";

type Params = {
	componentId: DeepReadonly<Ref<string>>;
	fieldKey: DeepReadonly<Ref<string>>;
	defaultValue?: DeepReadonly<Ref<string>>;
};

export function useComponentFieldViewModel(params: Params) {
	const wf = inject(injectionKeys.core);
	const ssbm = inject(injectionKeys.builderManager);

	const { setContentValue } = useComponentActions(wf, ssbm);

	const component = computed(() => {
		return wf.getComponentById(params.componentId.value);
	});

	function setFieldValue(value: string) {
		setContentValue(component.value.id, params.fieldKey.value, value);
	}

	const fieldValue = computed<string>(() => {
		return (
			component.value.content[params.fieldKey.value] ||
			params.defaultValue?.value ||
			""
		);
	});

	const fieldViewModel = computed<string>({
		get: () => fieldValue.value,
		set: (value: string) => {
			setFieldValue(value);
		},
	});

	return {
		setFieldValue,
		fieldValue,
		fieldViewModel,
	};
}
