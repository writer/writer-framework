<template>
	<div
		class="BuilderFieldsWriterApplicationId"
		:data-automation-key="props.fieldKey"
	>
		<component :is="selector" v-model="selected" />
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, PropType, defineAsyncComponent } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";

const BuilderApplicationSelect = defineAsyncComponent(
	() => import("../BuilderApplicationSelect.vue"),
);
const BuilderGraphSelect = defineAsyncComponent(
	() => import("../BuilderGraphSelect.vue"),
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

const selector = computed(() =>
	props.resourceType === "graph"
		? BuilderGraphSelect
		: BuilderApplicationSelect,
);

const selected = computed<string>({
	get: () => component.value.content[props.fieldKey] ?? "",
	set(value) {
		setContentValue(component.value.id, fieldKey.value, String(value));
	},
});
</script>
