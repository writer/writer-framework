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
				:component-id="componentId"
				:input-id="inputId"
				:value="inputValue"
				:placeholder="defaultValue"
				:type="inputType"
				:options
				:error
				:autofocus
				@input="handleInput"
			/>
		</template>
		<template v-else-if="templateField.control == FieldControl.Textarea">
			<BuilderTemplateInput
				multiline
				variant="text"
				class="content"
				:input-id="inputId"
				:component-id="componentId"
				:value="inputValue"
				:placeholder="defaultValue"
				:type="inputType"
				:error
				:autofocus
				@input="handleInput"
			/>
		</template>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, PropType, toRef } from "vue";
import { Component, FieldControl } from "@/writerTypes";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import injectionKeys from "@/injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";

const wf = inject(injectionKeys.core);

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
	autofocus: { type: Boolean },
	type: {
		type: String as PropType<"state" | "template" | "state-template">,
		required: false,
		default: "template",
	},
});

const templateField = computed(() => {
	const { type } = wf.getComponentById(props.componentId);
	const definition = wf.getComponentDefinition(type);
	return definition.fields[props.fieldKey];
});

const defaultValue = computed(() => templateField.value.default ?? "");

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
	defaultValue,
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
				acc[component.id] = component.id;
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
		return field.options(wf, props.componentId);
	}
	if (typeof field.options === "string") {
		return predefinedOptionFns?.[field.options](wf, props.componentId);
	}
	return field.options;
});

const inputType = computed(() =>
	["state", "state-template"].includes(props.type) ? "state" : "template",
);

const inputValue = computed(() => parseContentValue(fieldViewModel.value));

const handleInput = (ev: Event) => {
	fieldViewModel.value = transformToContentValue(
		(ev.target as HTMLInputElement).value,
	);
};

function transformToContentValue(value: unknown): string {
	if (typeof value !== "string") {
		return "";
	}

	if (props.type === "state-template") {
		return `@{${value}}`;
	}

	return value;
}

function parseContentValue(value: unknown): string {
	if (typeof value !== "string") {
		return "";
	}

	if (props.type === "state-template") {
		return value.replace(/^@{/, "").replace(/}$/, "");
	}

	return value;
}
</script>

<style>
.BuilderFieldsText .content {
	width: 100%;
}
</style>

<style scoped>
@import "../sharedStyles.css";
</style>
