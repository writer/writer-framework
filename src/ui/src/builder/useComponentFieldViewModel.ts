import { computed, inject, MaybeRef, ref, toValue, watch } from "vue";
import { BuilderManager, Core } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { useLogger } from "@/composables/useLogger";
import { useComponentActions } from "./useComponentActions";

type Params = {
	componentId: MaybeRef<string>;
	fieldKey: MaybeRef<string>;
	defaultValue?: MaybeRef<string | undefined>;
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

	const logger = useLogger();

	const component = computed(() => {
		return wf.getComponentById(toValue(params.componentId));
	});

	watch(
		component,
		(componentValue) => {
			if (!componentValue) {
				logger.error(
					`useComponentFieldViewModel: component with id "${toValue(params.componentId)}" not found`,
				);
			}
		},
		{
			immediate: true,
		},
	);

	const fallbackValue = computed<string>(() => {
		const defaultValue = toValue(params.defaultValue);

		if (typeof defaultValue === "string") {
			return defaultValue;
		}

		const compDef = wf.getComponentDefinition(component.value?.type);

		return compDef?.fields?.[toValue(params.fieldKey)]?.default ?? "";
	});

	const { setContentValue } = useComponentActions(wf, ssbm);

	function setFieldValue(value: string) {
		if (!component.value) {
			return;
		}

		setContentValue(component.value.id, toValue(params.fieldKey), value);
	}

	const isDirty = ref(false);

	watch(
		[() => toValue(params.componentId), () => toValue(params.fieldKey)],
		() => {
			isDirty.value = false;
		},
	);

	const fieldValue = computed<string>(() => {
		const val = component.value?.content?.[toValue(params.fieldKey)];

		if (isDirty.value && typeof val === "string") {
			return val;
		}

		return val || fallbackValue.value;
	});

	const fieldViewModel = computed<string>({
		get: () => fieldValue.value,
		set: (value: string) => {
			isDirty.value = true;

			setFieldValue(value);
		},
	});

	return fieldViewModel;
}
