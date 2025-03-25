<template>
	<div
		class="BuilderFieldsComponentEventType"
		:data-automation-key="props.fieldKey"
	>
		<WdsSelect
			v-if="options.length"
			v-model="selected"
			:options="options"
			hide-icons
		/>
		<WdsTextInput v-else v-model="selected" />
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, defineAsyncComponent } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import type { Option } from "@/wds/WdsSelect.vue";
import { FieldType } from "@/writerTypes";
import WdsTextInput from "@/wds/WdsTextInput.vue";

const WdsSelect = defineAsyncComponent(() => import("@/wds/WdsSelect.vue"));

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
});
const { componentId, fieldKey } = toRefs(props);

const component = computed(() => wf.getComponentById(componentId.value));
const componentDefinition = computed(() =>
	wf.getComponentDefinition(component.value?.type),
);

const options = computed<Option[]>(() => {
	// find the name of the field that specify the componentId
	const componentIdField = Object.entries(
		componentDefinition.value?.fields ?? {},
	)
		.find(([, field]) => field.type === FieldType.ComponentId)
		?.at(0);
	if (componentIdField === undefined) return [];

	const targetComponentId = component.value.content[String(componentIdField)];
	const targetComponent = wf.getComponentById(targetComponentId);
	const targetComponentDef = wf.getComponentDefinition(targetComponent?.type);

	if (!targetComponentDef?.events) return [];

	return Object.keys(targetComponentDef.events).map((key) => ({
		value: key,
		label: key,
	}));
});

const selected = computed<string>({
	get: () => component.value.content[props.fieldKey] ?? "",
	set(value) {
		setContentValue(component.value.id, fieldKey.value, String(value));
	},
});
</script>
