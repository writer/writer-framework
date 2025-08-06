<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import { useComponentDescription } from "../useComponentDescription";
import WdsDropdownMenuItem from "@/wds/WdsDropdownMenuItem.vue";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
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
	value: props.path,
}));

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

async function goToComponent() {
	await goToComponentParentPage(props.componentId);
	wfbm.setSelection(props.componentId);
}
</script>

<template>
	<WdsDropdownMenuItem
		class="BuilderStateSelectorDropdownItemComponent"
		:option="option"
		:selected="selected"
		show-custom-action
		@mousemove="isHovered = true"
		@mouseout="isHovered = false"
	>
		<template v-if="isHovered" #action>
			<WdsButton
				variant="neutral"
				size="smallIcon"
				data-writer-tooltip="Jump to this block"
				@click.prevent="goToComponent"
				@mousemove="isHovered = true"
			>
				<WdsIcon name="square-dashed-mouse-pointer" />
			</WdsButton>
		</template>
	</WdsDropdownMenuItem>
</template>
