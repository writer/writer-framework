import { computed, inject, MaybeRef, toValue } from "vue";
import { BuilderManager, Core } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { useComponentActions } from "./useComponentActions";

type Params = {
	componentId: MaybeRef<string>;
	fieldKey: MaybeRef<string>;
	defaultValue?: MaybeRef<string>;
};

type Dependencies = {
	wf?: Core;
	ssbm?: BuilderManager;
};

export function useComponentFieldViewModel(
	params: Params,
	dependencies?: Dependencies,
) {
	const wf = dependencies?.wf ?? inject(injectionKeys.core);
	const ssbm = dependencies?.ssbm ?? inject(injectionKeys.builderManager);

	if (!wf) {
		throw new Error("Missing core injection.");
	}

	if (!ssbm) {
		throw new Error("Missing builderManager injection.");
	}

	const { setContentValue } = useComponentActions(wf, ssbm);

	const component = computed(() => {
		return wf.getComponentById(toValue(params.componentId));
	});

	function setFieldValue(value: string) {
		setContentValue(component.value.id, toValue(params.fieldKey), value);
	}

	const fieldValue = computed<string>(() => {
		return (
			component.value.content[toValue(params.fieldKey)] ||
			toValue(params.defaultValue) ||
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
