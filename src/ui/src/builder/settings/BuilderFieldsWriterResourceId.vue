<template>
	<div
		class="BuilderFieldsWriterResourceId"
		:data-automation-key="props.fieldKey"
	>
		<component :is="selector" ref="selectorEl" v-model="selected" />
		<a
			v-if="ressourceUrl"
			class="BuilderFieldsWriterResourceId__link"
			:href="ressourceUrl"
			target="_blank"
			:data-writer-tooltip="linkTooltip"
			><i class="material-symbols-outlined"> open_in_new </i></a
		>
	</div>
</template>

<script setup lang="ts">
import {
	toRefs,
	inject,
	computed,
	PropType,
	defineAsyncComponent,
	useTemplateRef,
	watch,
} from "vue";
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

const selectorEl = useTemplateRef("selectorEl");

const selector = computed(() =>
	props.resourceType === "graph"
		? BuilderGraphSelect
		: BuilderApplicationSelect,
);

const linkTooltip = computed(() => {
	switch (props.resourceType) {
		case "graph":
			return "Edit knowledge graph";
		case "application":
			return "Edit agent";
		default:
			return undefined;
	}
});

const ressourceUrl = computed(() => {
	if (!selected.value) return;

	const orgId = selectorEl.value?.selectedData?.organization_id;
	if (!orgId) return;

	switch (props.resourceType) {
		case "graph": {
			const params = new URLSearchParams({ graphId: selected.value });
			return `https://app.writer.com/aistudio/organization/${orgId}/knowledge-graph?${params}`;
		}
		case "application":
			return `https://app.writer.com/aistudio/organization/${orgId}/app/${selected.value}`;
		default:
			return undefined;
	}
});

const selected = computed<string>({
	get: () => component.value.content[props.fieldKey] ?? "",
	set(value) {
		setContentValue(component.value.id, fieldKey.value, String(value));
	},
});

watch(
	() => selected.value,
	async (newAppId) => {
		if (props.resourceType !== "application" || !newAppId) return;

		const appData = selectorEl.value?.selectedData;
		const inputsList = appData?.inputs;

		if (!inputsList || typeof inputsList !== "object") return;

		setContentValue(
			component.value.id,
			"appInputs",
			JSON.stringify(inputsList),
		);
	},
);
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
