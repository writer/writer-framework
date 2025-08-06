<template>
	<div class="BuilderFieldsComponentId" :data-automation-key="props.fieldKey">
		<WdsSelect v-model="selected" :options="options" enable-search />
		<WdsButton
			v-if="selected"
			variant="neutral"
			size="smallIcon"
			data-writer-tooltip="Jump to the element"
			:disabled="!selectedComponent"
			@click="jumpToElement"
		>
			<WdsIcon name="square-dashed-mouse-pointer" />
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, defineAsyncComponent, toRef } from "vue";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import injectionKeys from "@/injectionKeys";
import type { Option } from "@/wds/WdsSelect.vue";
import { useComponentDescription } from "../useComponentDescription";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";

const WdsSelect = defineAsyncComponent(() => import("@/wds/WdsSelect.vue"));

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

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
			label: previewText.value || name.value,
			detail: previewText.value ? name.value : undefined,
			icon,
		});
	}

	return options;
});

const selected = computed<string, string | string[]>({
	get: () => fieldViewModel.value,
	set(value) {
		fieldViewModel.value = String(value);
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
