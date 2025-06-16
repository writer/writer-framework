<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { computed, inject, PropType } from "vue";
import type { PanelId } from "../builderManager";
import WdsButton from "@/wds/WdsButton.vue";

const props = defineProps({
	panelId: { type: String as PropType<PanelId>, required: true },
});

const wfbm = inject(injectionKeys.builderManager);

const isExpanded = computed(
	() => wfbm.openPanels.value.get(props.panelId) === "full",
);

const icon = computed(() => (isExpanded.value ? "hide" : "zoom_out_map"));

function toggle() {
	wfbm.openPanels.value.set(
		props.panelId,
		isExpanded.value ? "open" : "full",
	);
}
</script>

<template>
	<WdsButton
		variant="neutral"
		size="smallIcon"
		class="BuilderPanelExpanderBtn"
		@click="toggle"
	>
		<i class="material-symbols-outlined">{{ icon }}</i>
	</WdsButton>
</template>

<style lang="css" scoped>
.BuilderPanelExpanderBtn {
	min-width: 32px;
}
</style>
