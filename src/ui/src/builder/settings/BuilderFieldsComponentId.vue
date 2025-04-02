<template>
	<div class="BuilderFieldsComponentId" :data-automation-key="props.fieldKey">
		<BuilderSelect v-model="selected" :options="options" enable-search />
		<WdsButton
			v-if="selected"
			variant="neutral"
			size="smallIcon"
			data-writer-tooltip="Jump to the element"
			:disabled="!selectedComponent"
			@click="jumpToElement"
		>
			<i class="material-symbols-outlined">jump_to_element</i>
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, defineAsyncComponent } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import type { Option } from "../BuilderSelect.vue";
import { useComponentDescription } from "../useComponentDescription";
import WdsButton from "@/wds/WdsButton.vue";

const BuilderSelect = defineAsyncComponent(
	() => import("../BuilderSelect.vue"),
);

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

function* getComponents() {
	yield wf.getComponentById("root");
	yield* wf.getComponentsNested("root");
}

const options = computed<Option[]>(() => {
	const options: Option[] = [];

	for (const component of getComponents()) {
		const def = wf.getComponentDefinition(component?.type);
		if (!def?.events || Object.keys(def.events).length === 0) continue;

		const { name, previewText, possibleImageUrls } =
			useComponentDescription(wf, component);

		const icon = possibleImageUrls.value;
		const value = component.id;

		options.push({
			value,
			label: previewText.value ?? name.value,
			detail: previewText.value ? name.value : undefined,
			icon,
		});
	}

	return options;
});

const selected = computed<string>({
	get: () => component.value.content[props.fieldKey] ?? "",
	set(value) {
		setContentValue(component.value.id, fieldKey.value, String(value));
	},
});

const pageId = computed(() => {
	let current = selected.value;
	while (current) {
		const comp = wf.getComponentById(current);
		if (comp.type === "page") return comp.id;
		current = comp.parentId;
	}
	return undefined;
});

const selectedComponent = computed(() => wf.getComponentById(selected.value));

function jumpToElement() {
	if (!selected.value || !selectedComponent.value) return;
	if (pageId.value) {
		ssbm.mode.value = "ui";
		wf.setActivePageId(pageId.value);
	}
	ssbm.setSelection(selected.value, null, "click");
}
</script>

<style scoped>
.BuilderFieldsComponentId {
	display: grid;
	grid-template-columns: minmax(0, 1fr) auto;
	align-items: center;
	gap: 12px;
}
</style>
