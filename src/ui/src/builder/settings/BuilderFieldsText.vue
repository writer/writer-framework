<template>
	<div class="BuilderFieldsText" :data-automation-key="props.fieldKey">
		<template
			v-if="
				!templateField.control ||
				templateField.control == FieldControl.Text
			"
		>
			<BuilderTemplateInput
				class="content"
				:input-id="inputId"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				:options="options"
				:error="error"
				@input="handleInput"
			/>
		</template>
		<template v-else-if="templateField.control == FieldControl.Textarea">
			<BuilderTemplateInput
				multiline
				variant="text"
				class="content"
				:input-id="inputId"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				:error="error"
				@input="handleInput"
			/>
		</template>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, PropType } from "vue";
import { Component, FieldControl } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
});
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));
const templateField = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition.fields[fieldKey.value];
});

const inputId = computed(() => `${props.componentId}-${props.fieldKey}`);

const predefinedOptionFns = {
	uiComponents: () => {
		const uiComponents = wf
			.getComponents(undefined, { sortedByPosition: true })
			.filter((c) => wf.isChildOf("root", c.id));
		const options = {};
		uiComponents.forEach((component) => {
			options[component.id] = component.id;
		});
		return options;
	},
	uiComponentsWithEvents: () => {
		return wf
			.getComponents(undefined, { sortedByPosition: true })
			.filter((c) => wf.isChildOf("root", c.id))
			.filter((c) => Boolean(wf.getComponentDefinition(c.type).events))
			.reduce((acc, component) => {
				acc[component.id] = [component.id];
				return acc;
			}, {});
	},
	eventTypes: (core: typeof wf, componentId: Component["id"]) => {
		const refComponentId =
			core.getComponentById(componentId).content?.["refComponentId"];
		const refComponent = wf.getComponentById(refComponentId);
		if (!refComponent) return {};
		const refDef = core.getComponentDefinition(refComponent.type);
		const refEvents = Object.fromEntries(
			Object.keys(refDef.events ?? {}).map((k) => [k, k]),
		);
		return refEvents;
	},
};

const options = computed(() => {
	const field = templateField.value;
	if (!field.options) return {};
	if (typeof field.options === "function") {
		return field.options(wf, componentId.value);
	}
	if (typeof field.options === "string") {
		return predefinedOptionFns?.[field.options](wf, componentId.value);
	}
	return field.options;
});

const handleInput = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};
</script>

<style>
.BuilderFieldsText .content {
	width: 100%;
}
</style>

<style scoped>
@import "../sharedStyles.css";
</style>
