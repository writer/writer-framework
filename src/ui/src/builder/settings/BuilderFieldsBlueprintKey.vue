<template>
	<div class="BuilderFieldsBlueprintKey" :data-automation-key="props.fieldKey">
		<BuilderSelect v-model="selectedBlueprintKey" :options="options" />
		<WdsButton
			v-if="selectedBlueprintComponentId"
			variant="neutral"
			size="smallIcon"
			data-writer-tooltip="Jump to the blueprint"
			@click="jumpToBlueprint"
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

const selectedBlueprintKey = computed<string>({
	get: () => component.value?.content[props.fieldKey] ?? "",
	set: (key) => setContentValue(component.value.id, fieldKey.value, key),
});

const options = computed<Option[]>(() => {
	const worflowsKeys = new Set<string>();

	for (const page of wf.getComponents("blueprints_root")) {
		if (page.content.key) worflowsKeys.add(page.content.key);
	}

	const blueprintsOptions = [...worflowsKeys]
		.sort((a, b) => a.localeCompare(b))
		.map((key) => ({
			value: key,
			label: key,
			icon: "linked_services",
		}));

	const options: Option[] = [
		{ value: "", label: "(No blueprint)", icon: "block" },
		...blueprintsOptions,
	];

	// add an option if selected blueprint does not exists
	if (!options.some((o) => o.value === selectedBlueprintKey.value)) {
		const key = selectedBlueprintKey.value;
		options.push({ value: key, label: key });
	}

	return options;
});

const selectedBlueprintComponentId = computed<string | undefined>(() => {
	const component = wf
		.getComponents("blueprints_root")
		.find((page) => page.content.key === selectedBlueprintKey.value);
	return component?.id;
});

function jumpToBlueprint() {
	if (!selectedBlueprintComponentId.value) return;
	ssbm.setSelection(selectedBlueprintComponentId.value, null, "click");
	wf.setActivePageId(selectedBlueprintComponentId.value);
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsBlueprintKey {
	display: grid;
	grid-template-columns: minmax(0, 1fr) auto;
	align-items: center;
	gap: 12px;
}
</style>
