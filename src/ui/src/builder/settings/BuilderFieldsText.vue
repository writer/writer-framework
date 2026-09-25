<template>
	<div class="BuilderFieldsText" :data-automation-key="props.fieldKey">
		<template v-if="fieldControl == FieldControl.Text">
			<WdsSelect
				v-if="shouldUseDropdown"
				v-model="selectValue"
				class="content"
				:options="selectOptions"
				:placeholder="defaultValue"
				default-icon=""
			/>
			<BuilderTemplateInput
				v-else
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
		<template v-else-if="fieldControl == FieldControl.Textarea">
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
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";
import type { Option } from "@/wds/WdsSelect.vue";

const WdsSelect = defineAsyncComponentWithLoader({
	loader: () => import("@/wds/WdsSelect.vue"),
});

const wf = inject(injectionKeys.core);

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	fieldControl: {
		type: String as PropType<FieldControl>,
		required: false,
		default: FieldControl.Text,
	},
	defaultValue: { type: String, default: undefined },
	error: { type: String, required: false, default: undefined },
	autofocus: { type: Boolean },
	type: {
		type: String as PropType<"state" | "template" | "state-template">,
		required: false,
		default: "template",
	},
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
	defaultValue: toRef(props, "defaultValue"),
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
	pageKeys: () => {
		const pages = wf
			.getComponents("root", { sortedByPosition: true })
			.filter((component) => component.type === "page");
		return pages.reduce((acc, page) => {
			const key = page.content?.["key"];
			if (!key) {
				return acc;
			}
			const label =
				page.content?.["title"] ??
				page.content?.["name"] ??
				key ??
				page.id;
			acc[key] = label;
			return acc;
		}, {});
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

const options = computed<Record<string, string>>(() => {
	const component = wf.getComponentById(props.componentId);
	const componentDefinition = wf.getComponentDefinition(component.type);
	const field = componentDefinition.fields[props.fieldKey];

	if (!field.options) return {};
	if (typeof field.options === "function") {
		return field.options(wf, props.componentId);
	}
	if (typeof field.options === "string") {
		return predefinedOptionFns?.[field.options](wf, props.componentId);
	}
	return field.options;
});

const selectOptions = computed<Option[]>(() =>
	Object.entries(options.value ?? {}).map(([value, label]) => ({
		value,
		label,
	})),
);

const shouldUseDropdown = computed(
	() => props.type === "template" && selectOptions.value.length > 0,
);

const inputType = computed(() =>
	["state", "state-template"].includes(props.type) ? "state" : "template",
);

const inputValue = computed(() => parseContentValue(fieldViewModel.value));

const selectValue = computed<string | undefined>({
	get: () => {
		const value = inputValue.value;
		return selectOptions.value.some((option) => option.value === value)
			? value
			: undefined;
	},
	set(value) {
		fieldViewModel.value = transformToContentValue(value ?? "");
	},
});

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
