<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useComponentDescription } from "../useComponentDescription";
import WdsDropdownMenuItem from "@/wds/WdsDropdownMenuItem.vue";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import { useComponentActions } from "../useComponentActions";

const props = defineProps({
	componentId: { type: String, required: true },
	path: { type: String, required: true },
	selected: { type: Boolean, required: false },
});

const wf = inject(injectionKeys.core)!;
const wfbm = inject(injectionKeys.builderManager)!;

const isHovered = ref(false);

const component = computed(() => wf.getComponentById(props.componentId));

const { name, possibleImageUrls, previewText } = useComponentDescription(
	wf,
	component,
);

const option = computed<WdsDropdownMenuOption>(() => ({
	icon: possibleImageUrls.value,
	label: props.path,
	detail: previewText.value || name.value,
	value: props.componentId,
}));

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

async function goToComponent() {
	wfbm.setSelection(props.componentId);

	const pageId = await goToComponentParentPage(props.componentId);

	switch (wf.getComponentById(pageId)?.type) {
		case "page":
			wfbm.mode.value = "ui";
			break;
		case "blueprints_blueprint":
			wfbm.mode.value = "blueprints";
			break;
	}
}
</script>

<template>
	<WdsDropdownMenuItem
		class="BuilderStateSelectorDropdownItemComponent"
		:option="option"
		:selected="selected"
		@mousemove="isHovered = true"
		@mouseout="isHovered = false"
	>
		<template v-if="isHovered" #action>
			<i
				class="material-symbols-outlined"
				data-writer-tooltip="Expand"
				@click.prevent="goToComponent"
				@mousemove="isHovered = true"
				>open_in_new</i
			>
		</template>
	</WdsDropdownMenuItem>
</template>
