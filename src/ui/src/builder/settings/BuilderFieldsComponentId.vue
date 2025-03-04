<template>
	<div class="BuilderFieldsComponentId" :data-automation-key="props.fieldKey">
		<BuilderSelect v-model="selected" :options="options" enable-search />
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, PropType, defineAsyncComponent } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import type { Option } from "../BuilderSelect.vue";
import { useComponentDescription } from "../useComponentDescription";

const BuilderSelect = defineAsyncComponent(
	() => import("../BuilderSelect.vue"),
);

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
	resourceType: {
		type: String as PropType<"graph" | "application">,
		required: true,
	},
});
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const options = computed<Option[]>(() => {
	const options: Option[] = [];

	for (const component of wf.getComponentsNested("root")) {
		const { name, previewText, possibleImageUrls } =
			useComponentDescription(wf, component);
		if (previewText.value) {
			options.push({
				value: component.id,
				detail: name.value,
				label: previewText.value,
				icon: possibleImageUrls.value,
			});
		} else {
			options.push({
				value: component.id,
				label: name.value,
				icon: possibleImageUrls.value,
			});
		}
	}

	return options;
});

const selected = computed<string>({
	get: () => component.value.content[props.fieldKey] ?? "",
	set(value) {
		setContentValue(component.value.id, fieldKey.value, String(value));
	},
});
</script>
