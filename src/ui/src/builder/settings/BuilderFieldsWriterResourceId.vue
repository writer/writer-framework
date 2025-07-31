<template>
	<div class="BuilderFieldsWriterResourceId" :data-automation-key="fieldKey">
		<component
			:is="selector"
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
</template>

<script setup lang="ts">
import {
	inject,
	computed,
	PropType,
	defineAsyncComponent,
	useTemplateRef,
	ref,
} from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import WdsIcon from "@/wds/WdsIcon.vue";
import { WriterApplication } from "@/writerTypes";

const BuilderApplicationSelect = defineAsyncComponent(
	() => import("../BuilderApplicationSelect.vue"),
);
const BuilderGraphSelect = defineAsyncComponent(
	() => import("../BuilderGraphSelect.vue"),
);
const BuilderModelSelect = defineAsyncComponent(
	() => import("../BuilderModelSelect.vue"),
);

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	defaultValue: { type: String, required: false, default: undefined },
	error: { type: String, required: false, default: undefined },
	resourceType: {
		type: String as PropType<"graph" | "application" | "model">,
		required: true,
	},
	enableMultiSelection: { type: Boolean, required: false, default: false },
});

const component = computed(() => wf.getComponentById(props.componentId));

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
			const raw =
				component.value.content[props.fieldKey] ||
				props.defaultValue ||
				"[]";
			try {
				return JSON.parse(raw);
			} catch {
				return [];
			}
		}
		return (
			component.value.content[props.fieldKey] || props.defaultValue || ""
		);
	},
	set(value: string | string[]) {
		if (props.enableMultiSelection) {
			setContentValue(
				component.value.id,
				props.fieldKey,
				JSON.stringify(value),
			);
		} else {
			setContentValue(component.value.id, props.fieldKey, String(value));
		}
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

	setContentValue(
		component.value.id,
		"appInputs",
		JSON.stringify(appData.inputs),
	);
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsWriterResourceId {
	display: grid;
	grid-template-columns: minmax(0, 1fr) auto;
	align-items: center;
	gap: 12px;
}

.BuilderFieldsWriterResourceId__link {
	text-decoration: none;
	display: flex;
	align-items: center;
	font-size: 18px;
}
</style>
