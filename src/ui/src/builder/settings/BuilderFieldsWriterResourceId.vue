<template>
	<WdsFieldWrapper
		:is-binding-button-shown
		:is-binding-enabled="isBindingMode"
		:label
		:unit
		:hint
		:error
		:data-automation-key="fieldKey"
		@update:is-binding-enabled="toggleBindingMode"
	>
		<div
			class="BuilderFieldsWriterResourceId"
			:data-automation-key="fieldKey"
		>
			<BuilderFieldsText
				v-if="isBindingMode"
				type="state-template"
				:component-id
				:field-key
				:error
				default-value=""
			/>
			<component
				:is="selector"
				v-else
				ref="selectorEl"
				v-model="selected"
				:enable-multi-selection="enableMultiSelection"
				@selected-data="onSelectedData"
			/>
			<a
				v-if="ressourceUrl"
				class="BuilderFieldsWriterResourceId__link"
				:href="ressourceUrl"
				target="_blank"
				:data-writer-tooltip="linkTooltip"
			>
				<WdsIcon name="external-link" />
			</a>
		</div>
	</WdsFieldWrapper>
</template>

<script setup lang="ts">
import {
	computed,
	PropType,
	defineAsyncComponent,
	useTemplateRef,
	ref,
	toRef,
} from "vue";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import { useBindingMode } from "./composables/useBindingMode";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import { WriterApplication } from "@/writerTypes";
import BuilderFieldsText from "./BuilderFieldsText.vue";

const BuilderApplicationSelect = defineAsyncComponent(
	() => import("../BuilderApplicationSelect.vue"),
);
const BuilderGraphSelect = defineAsyncComponent(
	() => import("../BuilderGraphSelect.vue"),
);
const BuilderModelSelect = defineAsyncComponent(
	() => import("../BuilderModelSelect.vue"),
);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	label: { type: String, required: false, default: undefined },
	unit: { type: String, required: false, default: undefined },
	hint: { type: String, required: false, default: undefined },
	error: { type: String, required: false, default: undefined },
	resourceType: {
		type: String as PropType<"graph" | "application" | "model">,
		required: true,
	},
	enableMultiSelection: { type: Boolean, required: false, default: false },
	isBindingButtonShown: { type: Boolean, required: false, default: false },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

const { isBindingMode, toggleBindingMode } = useBindingMode({
	fieldViewModel,
});

const appInputsViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: "appInputs",
});

const selectorEl = useTemplateRef("selectorEl");

const selector = computed(() => {
	switch (props.resourceType) {
		case "model":
			return BuilderModelSelect;
		case "graph":
			return BuilderGraphSelect;
		case "application":
			return BuilderApplicationSelect;
		default:
			throw new Error(`Unexpected resourceType: ${props.resourceType}`);
	}
});

const linkTooltip = computed(() => {
	switch (props.resourceType) {
		case "graph":
			return "Edit knowledge graph";
		case "application":
			return "Edit agent";
		case "model":
			return "About models";
		default:
			return undefined;
	}
});

const ressourceUrl = computed(() => {
	if (Array.isArray(selected.value)) return;
	const value = selected.value;
	if (!value) return;

	const orgId = selectorEl.value?.selectedData?.organization_id;
	if (!orgId) return;

	switch (props.resourceType) {
		case "graph": {
			const params = new URLSearchParams({ graphId: value });
			return `https://app.writer.com/aistudio/organization/${orgId}/knowledge-graph?${params}`;
		}
		case "application":
			return `https://app.writer.com/aistudio/organization/${orgId}/app/${value}`;
		case "model":
			return `https://dev.writer.com/home/models#model-overview`;
		default:
			return undefined;
	}
});

const selected = computed<string | string[]>({
	get() {
		if (props.enableMultiSelection) {
			const raw = fieldViewModel.value || "[]";
			try {
				return JSON.parse(raw);
			} catch {
				return [];
			}
		}
		return fieldViewModel.value;
	},
	set(value: string | string[]) {
		fieldViewModel.value = props.enableMultiSelection
			? JSON.stringify(value)
			: String(value);
	},
});

const selectedData = ref<WriterApplication | undefined>();

function onSelectedData(appData: WriterApplication | undefined) {
	selectedData.value = appData; // for readability
	if (
		props.resourceType !== "application" ||
		!appData ||
		!appData.inputs ||
		typeof appData.inputs !== "object"
	) {
		return;
	}

	appInputsViewModel.value = JSON.stringify(appData.inputs);
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsWriterResourceId {
	display: grid;
	grid-template-columns: 1fr;
	align-items: center;
	gap: 12px;
}

.BuilderFieldsWriterResourceId:has(.BuilderFieldsWriterResourceId__link) {
	grid-template-columns: 1fr auto;
}

.BuilderFieldsWriterResourceId__link {
	text-decoration: none;
	display: flex;
	align-items: center;
	font-size: 18px;
}
</style>
