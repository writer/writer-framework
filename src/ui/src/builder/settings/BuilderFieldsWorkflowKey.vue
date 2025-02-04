<template>
	<div class="BuilderFieldsWorkflowKey" :data-automation-key="props.fieldKey">
		<BuilderSelect v-model="selectedWorkflowKey" :options="options" />
		<WdsButton
			v-if="selectedWorkflowComponentId"
			variant="neutral"
			size="smallIcon"
			data-writer-tooltip="Jump to the workflow"
			@click="jumpToWorkflow"
		>
			<i class="material-symbols-outlined">jump_to_element</i>
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, defineAsyncComponent } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import { Option } from "../BuilderSelect.vue";

const BuilderSelect = defineAsyncComponent(
	() => import("../BuilderSelect.vue"),
);

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
});

const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const selectedWorkflowKey = computed<string>({
	get: () => component.value?.content[props.fieldKey] ?? "",
	set: (key) => setContentValue(component.value.id, fieldKey.value, key),
});

const options = computed<Option[]>(() => {
	const worflowsKeys = new Set<string>();

	for (const page of wf.getComponents("workflows_root")) {
		if (page.content.key) worflowsKeys.add(page.content.key);
	}

	const workflowsOptions = [...worflowsKeys]
		.sort((a, b) => a.localeCompare(b))
		.map((key) => ({
			value: key,
			label: key,
			icon: "linked_services",
		}));

	const options: Option[] = [
		{ value: "", label: "(No workflow)", icon: "block" },
		...workflowsOptions,
	];

	// add an option if selected workflow does not exists
	if (!options.some((o) => o.value === selectedWorkflowKey.value)) {
		const key = selectedWorkflowKey.value;
		options.push({ value: key, label: key });
	}

	return options;
});

const selectedWorkflowComponentId = computed<string | undefined>(() => {
	const component = wf
		.getComponents("workflows_root")
		.find((page) => page.content.key === selectedWorkflowKey.value);
	return component?.id;
});

function jumpToWorkflow() {
	if (!selectedWorkflowComponentId.value) return;
	ssbm.setSelection(selectedWorkflowComponentId.value, null, "click");
	wf.setActivePageId(selectedWorkflowComponentId.value);
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsWorkflowKey {
	display: grid;
	grid-template-columns: 1fr auto;
	align-items: center;
	gap: 12px;
}
</style>
